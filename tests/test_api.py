import io

import pytest
from PIL import Image

from src import api, storage
from src.embeddings import ModelUnavailable


def payload(kind="lost"):
    return dict(report_type=kind, name="Wireless earbuds", category="Electronics",
                description="Dark Apple earbuds case with a white scratch", location="Main Library",
                location_detail="Second floor near desk 14", event_date="2026-09-20",
                identifying_details="White scratch on front-right edge",
                handover_location="Campus Security" if kind == "found" else None)


def test_crud_and_baseline(client):
    assert client.get("/health").status_code == 200
    lost = client.post("/items", json=payload()).json()
    found_response = client.post("/items", json=payload("found"))
    assert found_response.status_code == 201
    found = found_response.json()
    assert len(client.get("/items?report_type=lost").json()) == 1
    assert client.get(f"/items/{lost['id']}").json()["name"] == "Wireless earbuds"
    result = client.get(f"/matches/{lost['id']}?method=baseline").json()
    assert result["matches"][0]["item"]["id"] == found["id"]
    assert result["matches"][0]["score"] == pytest.approx(1)
    assert result["matches"][0]["components"]["image"] is None
    assert client.get(f"/matches/{found['id']}?method=baseline").status_code == 422
    assert client.put(f"/items/{lost['id']}", json=payload() | {"name": "Updated"}).json()["name"] == "Updated"
    assert client.delete(f"/items/{lost['id']}").status_code == 204
    assert client.get(f"/items/{lost['id']}").status_code == 404


def test_validation(client):
    for override in ({"report_type": "invalid"}, {"name": " "}, {"event_date": "not-a-date"}, {"category": "unknown"}, {"location": "Airport"}, {"image_path": "../../secret"}):
        assert client.post("/items", json=payload() | override).status_code == 422
    assert client.get("/items?limit=0").status_code == 422
    assert client.get("/items?report_type=oops").status_code == 422


def test_image_validation_storage_replacement_and_deletion(client):
    item = client.post("/items", json=payload()).json()
    url = f"/items/{item['id']}/image"
    assert client.post(url, files={"file": ("fake.png", b"not an image", "image/png")}).status_code == 422
    assert client.get(url).status_code == 404
    content = io.BytesIO()
    Image.new("RGB", (30, 30), "blue").save(content, format="PNG")
    response = client.post(url, files={"file": ("../../unsafe.png", content.getvalue(), "image/png")})
    assert response.status_code == 200
    assert response.json()["image_available"] is True
    first = next(storage.UPLOAD_DIR.iterdir())
    assert first.exists()
    assert client.get(url).headers["content-type"] == "image/jpeg"
    response = client.post(url, files={"file": ("new.png", content.getvalue(), "image/png")})
    second = next(path for path in storage.UPLOAD_DIR.iterdir())
    assert not first.exists() and second.exists()
    assert client.delete(f"/items/{item['id']}").status_code == 204
    assert not second.exists()


def test_found_privacy_matching_and_claim_workflow(client):
    lost = client.post("/items", json=payload()).json()
    found = client.post("/items", json=payload("found")).json()
    image = io.BytesIO()
    Image.new("RGB", (30, 30), "black").save(image, format="PNG")
    assert client.post(f"/items/{found['id']}/image", files={"file": ("found.png", image.getvalue(), "image/png")}).status_code == 200
    private_values = ["Dark Apple earbuds case", "desk 14", "front-right edge"]
    for body in (found, client.get("/items?report_type=found").json()[0],
                 client.get(f"/items/{found['id']}").json(),
                 client.get(f"/matches/{lost['id']}?method=baseline").json()["matches"][0]["item"]):
        serialized = str(body)
        assert body.get("description") is None
        assert body.get("image_available") is False
        assert "image_path" not in body and "location_detail" not in body and "identifying_details" not in body
        assert all(value not in serialized for value in private_values)
    assert client.get(f"/items/{found['id']}/image").status_code == 404

    created = client.post("/claims", json={"lost_report_id": lost["id"], "found_report_id": found["id"],
                                            "verification_response": "White scratch on the front-right edge"})
    assert created.status_code == 201 and created.json()["status"] == "pending"
    claim_id = created.json()["id"]
    assert client.get("/staff/claims").status_code == 403
    staff = client.get("/staff/claims", headers={"X-Staff-Key": "demo-staff-key"}).json()[0]
    assert staff["found_item"]["identifying_details"] == "White scratch on front-right edge"
    assert staff["found_item"]["location_detail"] == "Second floor near desk 14"
    approved = client.put(f"/staff/claims/{claim_id}", headers={"X-Staff-Key": "demo-staff-key"},
                          json={"status": "approved", "collection_point": "Campus Security"})
    assert approved.json()["status"] == "approved"
    assert client.get(f"/claims/{claim_id}").json()["collection_point"] == "Campus Security"


def test_model_error_is_not_silently_replaced(client, monkeypatch):
    def unavailable(*args, **kwargs):
        raise ModelUnavailable("Test model unavailable")
    monkeypatch.setattr(api, "rank_reports", unavailable)
    item = client.post("/items", json=payload()).json()
    response = client.get(f"/matches/{item['id']}")
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"]


def test_storage_limits_and_paths(monkeypatch):
    with pytest.raises(ValueError):
        storage.image_file("../secret.jpg")
    monkeypatch.setattr(storage, "MAX_IMAGE_BYTES", 2)
    with pytest.raises(ValueError, match="8 MB"):
        storage.save_image(b"abcd")
