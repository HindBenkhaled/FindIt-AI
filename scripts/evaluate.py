"""Measured retrieval experiments. Never substitute a baseline for failed AI."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
from datetime import date, datetime, timezone
from types import SimpleNamespace

from scripts.generate_data import DEST, generate
from src.config import (EARLY_FOUND_PENALTY, HIGH_MATCH, IMAGE_MODEL, POSSIBLE_MATCH,
                        ROOT, TEXT_MODEL, TIME_DECAY_DAYS, WEIGHTS)
from src.services import rank_reports

METHODS = ["keyword", "baseline", "text", "image", "text_image", "full"]


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def cached_revision(model_name: str) -> str | None:
    """Record the resolved local model snapshot without downloading anything."""
    try:
        from huggingface_hub import try_to_load_from_cache
        from pathlib import Path
        path = try_to_load_from_cache(model_name, "modules.json")
        return Path(path).parent.name if isinstance(path, str) else None
    except ImportError:
        return None


def retrieval_metrics(rankings: dict[int, list[int]], truth: dict[str, list[int]]) -> dict[str, float]:
    """Macro Recall@K and MRR; unreturned relevant items count as misses."""
    if not rankings:
        raise ValueError("Evaluation requires at least one query")
    totals = {"Recall@1": 0.0, "Recall@3": 0.0, "Recall@5": 0.0, "MRR": 0.0}
    for query_id, ranked_ids in rankings.items():
        relevant = set(truth[str(query_id)])
        if not relevant:
            raise ValueError("Every evaluation query needs a relevant item")
        for k in (1, 3, 5):
            totals[f"Recall@{k}"] += len(set(ranked_ids[:k]) & relevant) / len(relevant)
        first = next((i for i, item_id in enumerate(ranked_ids, 1) if item_id in relevant), None)
        totals["MRR"] += 1 / first if first else 0
    return {name: value / len(rankings) for name, value in totals.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=METHODS)
    args = parser.parse_args()
    source = DEST / "reports.json"
    if not source.exists():
        generate()
    data = json.loads(source.read_text(encoding="utf-8"))
    reports = [SimpleNamespace(**{**r, "event_date": date.fromisoformat(r["event_date"]) if r["event_date"] else None}) for r in data["reports"]]
    output = ROOT / "data" / "evaluation"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    # Common image-complete cohort keeps the five requested methods comparable.
    # A second cohort explicitly exercises missing images/location/time.
    for cohort in ("image_complete", "all_reports"):
        pool = [r for r in reports if cohort == "all_reports" or r.image_path]
        queries = [r for r in pool if r.report_type == "lost"]
        candidates = [r for r in pool if r.report_type == "found"]
        methods = args.methods if cohort == "image_complete" else [m for m in args.methods if m != "image"]
        for method in methods:
            record = {"cohort": cohort, "method": method, "queries": len(queries), "candidates": len(candidates)}
            print(f"Running {cohort}: {method} ({len(queries)} queries)", flush=True)
            try:
                rankings, predictions = {}, {}
                for query in queries:
                    ranked = rank_reports(query, candidates, method, resolve_image=lambda name: DEST / name)
                    rankings[query.id] = [r["item"].id for r in ranked]
                    predictions[query.id] = [{"item_id": r["item"].id, **{k: v for k, v in r.items() if k != "item"}} for r in ranked]
                record.update(status="ok", metrics=retrieval_metrics(rankings, data["relevant_pairs"]), rankings=rankings, predictions=predictions)
                print(record["metrics"], flush=True)
            except Exception as exc:
                # Preserve failed experiments rather than inventing scores or dropping rows.
                record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
                print(record["error"], flush=True)
            results.append(record)
            artifact = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "dataset_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "image_sha256": {r.image_path: hashlib.sha256((DEST / r.image_path).read_bytes()).hexdigest() for r in reports if r.image_path},
                "python": platform.python_version(), "text_model": TEXT_MODEL, "image_model": IMAGE_MODEL,
                "packages": {p: package_version(p) for p in ("sentence-transformers", "transformers", "torch", "numpy")},
                "cached_model_revisions": {m: cached_revision(m) for m in (TEXT_MODEL, IMAGE_MODEL)},
                "time_decay_days": TIME_DECAY_DAYS, "early_found_penalty": EARLY_FOUND_PENALTY,
                "label_thresholds": {"high": HIGH_MATCH, "possible": POSSIBLE_MATCH},
                "weights": WEIGHTS, "seed": data["seed"], "results": results,
                "limitations": "Tiny synthetic development benchmark; procedural images share templates. No held-out real data, no calibrated scores. Weights were chosen heuristically, not fitted.",
            }
            (output / "results.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    lines = ["# Measured synthetic retrieval results", "", artifact["limitations"], "",
             "Image-complete cohort: identical queries and candidate pool across methods. All-reports cohort includes missing data; image-only is inapplicable to its imageless queries.", "",
             "| Cohort | Method | Queries | Candidates | Recall@1 | Recall@3 | Recall@5 | MRR |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in results:
        metrics = " | ".join(f"{row['metrics'][k]:.3f}" for k in ("Recall@1", "Recall@3", "Recall@5", "MRR")) if row["status"] == "ok" else "failed | failed | failed | failed"
        lines.append(f"| {row['cohort']} | {row['method']} | {row['queries']} | {row['candidates']} | {metrics} |")
    for row in results:
        if row["status"] != "ok":
            lines.extend(["", f"{row['cohort']} / {row['method']}: {row['error']}"])
    lines.extend(["", f"Run timestamp: {artifact['created_at']}", "", "Full rankings, package versions, model identifiers and data hashes: `results.json`."])
    (output / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if any(row["status"] != "ok" for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
