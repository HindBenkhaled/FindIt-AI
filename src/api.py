"""FastAPI routes. Public routes never serialize private found-item fields."""
import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.config import MAX_IMAGE_BYTES, STAFF_KEY
from src.database import Claim, Item, get_session, init_db
from src.embeddings import ModelUnavailable
from src.schemas import (ClaimCreate, ClaimPublicRead, ClaimReview, ClaimStaffRead, ItemCreate,
                         MatchesRead, Method, PublicItemPreview, ReportType)
from src.services import rank_reports
from src.storage import image_file, save_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FindIt AI", version="0.2.0", lifespan=lifespan,
              description="Privacy-aware campus lost-and-found MVP. Scores are rankings, not probabilities.")
DB = Annotated[Session, Depends(get_session)]


def require_item(session: Session, item_id: int) -> Item:
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(404, "Report not found")
    return item


def require_staff(x_staff_key: Annotated[str | None, Header()] = None) -> None:
    if x_staff_key != STAFF_KEY:
        raise HTTPException(403, "Campus staff access required")


def public_item(item: Item) -> dict:
    found = item.report_type == "found"
    return {
        "id": item.id, "report_type": item.report_type, "name": item.name,
        "category": item.category, "description": None if found else item.description,
        "location": item.location, "event_date": item.event_date,
        "image_available": bool(item.image_path) and not found, "created_at": item.created_at,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "FindIt AI campus", "models": "lazy-loaded"}


@app.post("/items", response_model=PublicItemPreview, status_code=201)
def create_item(payload: ItemCreate, session: DB):
    if payload.report_type == "lost" and payload.handover_location:
        raise HTTPException(422, "Handover location applies only to found reports")
    item = Item(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return public_item(item)


@app.get("/items", response_model=list[PublicItemPreview])
def list_items(session: DB, report_type: ReportType | None = None,
               limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    statement = select(Item)
    if report_type:
        statement = statement.where(Item.report_type == report_type)
    items = session.scalars(statement.order_by(Item.id.desc()).offset(offset).limit(limit)).all()
    return [public_item(item) for item in items]


@app.get("/items/{item_id}", response_model=PublicItemPreview)
def read_item(item_id: int, session: DB):
    return public_item(require_item(session, item_id))


@app.put("/items/{item_id}", response_model=PublicItemPreview)
def update_item(item_id: int, payload: ItemCreate, session: DB):
    item = require_item(session, item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    session.commit()
    session.refresh(item)
    return public_item(item)


@app.post("/items/{item_id}/image", response_model=PublicItemPreview)
def upload_image(item_id: int, session: DB, file: UploadFile = File(...)):
    item = require_item(session, item_id)
    try:
        content = file.file.read(MAX_IMAGE_BYTES + 1)
        name = save_image(content)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        file.file.close()
    old_name = item.image_path
    item.image_path = name
    try:
        session.commit()
    except Exception:
        session.rollback()
        image_file(name).unlink(missing_ok=True)
        raise
    if old_name:
        image_file(old_name).unlink(missing_ok=True)
    session.refresh(item)
    return public_item(item)


@app.get("/items/{item_id}/image")
def read_image(item_id: int, session: DB):
    item = require_item(session, item_id)
    if item.report_type == "found":
        raise HTTPException(404, "Image not publicly available")
    if not item.image_path or not image_file(item.image_path).is_file():
        raise HTTPException(404, "Image not found")
    return FileResponse(image_file(item.image_path), media_type="image/jpeg")


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, session: DB):
    item = require_item(session, item_id)
    image_name = item.image_path
    session.delete(item)
    session.commit()
    if image_name:
        image_file(image_name).unlink(missing_ok=True)
    return Response(status_code=204)


@app.get("/matches/{item_id}", response_model=MatchesRead)
def find_matches(item_id: int, session: DB, method: Method = "full", top_k: int = Query(5, ge=1, le=100)):
    query = require_item(session, item_id)
    candidates = session.scalars(select(Item).where(Item.report_type == "found").order_by(Item.id)).all()
    try:
        ranked = rank_reports(query, candidates, method)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except ModelUnavailable as exc:
        raise HTTPException(503, str(exc)) from exc
    safe = [{**result, "item": public_item(result["item"])} for result in ranked[:top_k]]
    return {"query_id": item_id, "method": method, "candidate_count": len(candidates),
            "excluded_count": len(candidates) - len(ranked), "matches": safe}


@app.post("/claims", response_model=ClaimPublicRead, status_code=201)
def create_claim(payload: ClaimCreate, session: DB):
    lost = require_item(session, payload.lost_report_id)
    found = require_item(session, payload.found_report_id)
    if lost.report_type != "lost" or found.report_type != "found":
        raise HTTPException(422, "A claim must connect one lost report with one found report")
    claim = Claim(**payload.model_dump())
    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim


@app.get("/claims/{claim_id}", response_model=ClaimPublicRead)
def read_claim(claim_id: int, session: DB):
    claim = session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(404, "Claim not found")
    return claim


@app.get("/staff/claims", response_model=list[ClaimStaffRead], dependencies=[Depends(require_staff)])
def list_claims(session: DB):
    statement = select(Claim).options(joinedload(Claim.lost_item), joinedload(Claim.found_item)).order_by(Claim.id.desc())
    return session.scalars(statement).all()


@app.put("/staff/claims/{claim_id}", response_model=ClaimPublicRead, dependencies=[Depends(require_staff)])
def review_claim(claim_id: int, payload: ClaimReview, session: DB):
    claim = session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(404, "Claim not found")
    if payload.status == "approved":
        found = require_item(session, claim.found_report_id)
        claim.collection_point = payload.collection_point or found.handover_location
        if not claim.collection_point:
            raise HTTPException(422, "An approved claim needs a campus collection point")
    else:
        claim.collection_point = None
    claim.status = payload.status
    session.commit()
    session.refresh(claim)
    return claim
