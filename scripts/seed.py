"""Seed only an empty database; never overwrite user reports."""
import json

from sqlalchemy import func, select

from scripts.generate_data import DEST, generate
from src.database import Item, SessionLocal, init_db
from src.schemas import ItemCreate
from src.storage import image_file, save_image


def main():
    init_db()
    with SessionLocal() as session:
        if session.scalar(select(func.count()).select_from(Item)):
            print("Database already contains reports; seed skipped. No records changed.")
            return
        source = DEST / "reports.json"
        data = json.loads(source.read_text(encoding="utf-8")) if source.exists() else generate()
        stored_images = []
        try:
            for report in data["reports"]:
                payload = ItemCreate.model_validate({k: v for k, v in report.items() if k not in {"id", "image_path"}})
                name = save_image((DEST / report["image_path"]).read_bytes()) if report["image_path"] else None
                if name:
                    stored_images.append(name)
                session.add(Item(id=report["id"], image_path=name, **payload.model_dump()))
            session.commit()
        except Exception:
            session.rollback()
            for name in stored_images:
                image_file(name).unlink(missing_ok=True)
            raise
    print(f"Seeded {len(data['reports'])} explicitly synthetic reports.")


if __name__ == "__main__":
    main()
