"""Loading and integrity validation for versioned retrieval benchmarks."""
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace


def load_split(root: Path, split: str) -> tuple[list[SimpleNamespace], dict[str, dict]]:
    split_dir = root / split
    reports_doc = json.loads((split_dir / "reports.json").read_text(encoding="utf-8"))
    qrels_doc = json.loads((split_dir / "qrels.json").read_text(encoding="utf-8"))
    if reports_doc.get("split") != split or qrels_doc.get("split") != split:
        raise ValueError("Benchmark files do not match requested split")
    raw_reports, qrels = reports_doc["reports"], qrels_doc["qrels"]
    ids = [report["id"] for report in raw_reports]
    if len(ids) != len(set(ids)):
        raise ValueError("Report IDs must be unique within a split")
    by_id = {report["id"]: report for report in raw_reports}
    for query_id, label in qrels.items():
        query = by_id.get(int(query_id))
        if not query or query["report_type"] != "lost":
            raise ValueError(f"Qrel query {query_id} must reference a lost report")
        if not label.get("relevant"):
            raise ValueError(f"Query {query_id} has no relevant found reports")
        for candidate_id in label["relevant"] + label.get("hard_negatives", []):
            candidate = by_id.get(candidate_id)
            if not candidate or candidate["report_type"] != "found":
                raise ValueError(f"Candidate {candidate_id} must reference a found report")
        if set(label["relevant"]) & set(label.get("hard_negatives", [])):
            raise ValueError(f"Query {query_id} labels one report as both relevant and negative")
    for report in raw_reports:
        image_path = report.get("image_path")
        if image_path and not (split_dir / image_path).is_file():
            raise ValueError(f"Missing image: {split}/{image_path}")
    test_dir = root / "test"
    if split == "dev" and (test_dir / "reports.json").exists():
        test_ids = {r["id"] for r in json.loads((test_dir / "reports.json").read_text(encoding="utf-8"))["reports"]}
        if set(ids) & test_ids:
            raise ValueError("Development and test report IDs overlap")
    reports = [SimpleNamespace(**{**report, "event_date": date.fromisoformat(report["event_date"]) if report.get("event_date") else None}) for report in raw_reports]
    return reports, qrels
