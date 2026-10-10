"""Loading and validation for exact-object image retrieval benchmarks."""
import hashlib
import json
from pathlib import Path

from src.config import ROOT


def load_protocol(root: Path, setting: str) -> tuple[list[dict], list[dict], dict, str]:
    queries = json.loads((root / "queries.json").read_text(encoding="utf-8"))
    gallery_path, qrels_path = root / f"gallery_{setting}.json", root / f"qrels_{setting}.json"
    gallery = json.loads(gallery_path.read_text(encoding="utf-8"))
    qrels = json.loads(qrels_path.read_text(encoding="utf-8"))
    validate_protocol(queries, gallery, qrels)
    digest = hashlib.sha256((root / "queries.json").read_bytes() + gallery_path.read_bytes() + qrels_path.read_bytes()).hexdigest()
    return queries, gallery, qrels, digest


def validate_protocol(queries: list[dict], gallery: list[dict], qrels: dict) -> None:
    query_ids, gallery_ids = {x["id"] for x in queries}, {x["id"] for x in gallery}
    if len(query_ids) != len(queries) or len(gallery_ids) != len(gallery):
        raise ValueError("Query and gallery IDs must be unique")
    if query_ids & gallery_ids:
        raise ValueError("A query image must never occur in its candidate gallery")
    query_by_id, gallery_by_id = {x["id"]: x for x in queries}, {x["id"]: x for x in gallery}
    if set(qrels) != query_ids:
        raise ValueError("Every query must have exactly one qrels entry")
    for query_id, labels in qrels.items():
        relevant = labels.get("relevant", [])
        if not relevant or not set(relevant) <= gallery_ids:
            raise ValueError(f"Invalid relevance IDs for {query_id}")
        if any(gallery_by_id[item]["object_id"] != query_by_id[query_id]["object_id"] for item in relevant):
            raise ValueError(f"Cross-object relevance label for {query_id}")
        expected = {x["id"] for x in gallery if x["object_id"] == query_by_id[query_id]["object_id"]}
        if set(relevant) != expected:
            raise ValueError(f"Qrels must include every same-object gallery image for {query_id}")
    for item in queries + gallery:
        if not (ROOT / item["path"]).is_file():
            raise ValueError(f"Missing image: {item['path']}")
