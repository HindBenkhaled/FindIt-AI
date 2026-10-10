"""Evaluate the unchanged production ranker on a versioned benchmark split."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.benchmark import load_split
from src.config import IMAGE_MODEL, ROOT, TEXT_MODEL, WEIGHTS
from src.services import rank_reports

METHODS = ["baseline", "text", "image", "text_image", "full"]


def retrieval_metrics(rankings: dict[int, list[int]], qrels: dict[str, dict]) -> dict[str, float]:
    if not rankings:
        raise ValueError("Evaluation requires at least one query")
    totals = {"Recall@1": 0.0, "Recall@3": 0.0, "Recall@5": 0.0, "MRR": 0.0}
    for query_id, ranked_ids in rankings.items():
        relevant = set(qrels[str(query_id)]["relevant"])
        for k in (1, 3, 5):
            totals[f"Recall@{k}"] += len(set(ranked_ids[:k]) & relevant) / len(relevant)
        rank = next((index for index, item_id in enumerate(ranked_ids, 1) if item_id in relevant), None)
        totals["MRR"] += 1 / rank if rank else 0
    return {key: value / len(rankings) for key, value in totals.items()}


def challenge_metrics(rankings: dict[int, list[int]], qrels: dict[str, dict]) -> dict[str, dict[str, float]]:
    groups = defaultdict(dict)
    tags = sorted({tag for query_id in rankings for tag in qrels[str(query_id)].get("challenge_tags", [])})
    for tag in tags:
        subset = {query_id: ranking for query_id, ranking in rankings.items() if tag in qrels[str(query_id)].get("challenge_tags", [])}
        if subset:
            groups[tag] = {"queries": len(subset), **retrieval_metrics(subset, qrels)}
    return dict(groups)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def evaluate(root: Path, split: str, methods: list[str]) -> dict:
    reports, qrels = load_split(root, split)
    split_dir = root / split
    queries_all = [report for report in reports if report.report_type == "lost"]
    candidates_all = [report for report in reports if report.report_type == "found"]
    by_id = {report.id: report for report in reports}
    results = []
    for cohort in ("image_complete", "all_reports"):
        if cohort == "image_complete":
            candidates = [candidate for candidate in candidates_all if candidate.image_path]
            queries = [query for query in queries_all if query.image_path and all(by_id[item_id].image_path for item_id in qrels[str(query.id)]["relevant"])]
            cohort_methods = methods
        else:
            candidates, queries = candidates_all, queries_all
            cohort_methods = [method for method in methods if method != "image"]
        for method in cohort_methods:
            record = {"split": split, "cohort": cohort, "method": method,
                      "queries": len(queries), "candidates": len(candidates)}
            print(f"Running {split}/{cohort}: {method} ({len(queries)} queries, {len(candidates)} candidates)", flush=True)
            try:
                # Untimed pass loads models and primes every query/candidate embedding.
                # The measured pass therefore captures warm-cache ranking latency.
                for query in queries:
                    rank_reports(query, candidates, method, resolve_image=lambda name: split_dir / name)
                rankings, predictions, latencies = {}, {}, []
                for query in queries:
                    started = time.perf_counter()
                    ranked = rank_reports(query, candidates, method, resolve_image=lambda name: split_dir / name)
                    latencies.append((time.perf_counter() - started) * 1000)
                    rankings[query.id] = [result["item"].id for result in ranked]
                    predictions[str(query.id)] = [{"item_id": result["item"].id, "score": result["score"],
                                                    "label": result["label"], "components": result["components"],
                                                    "effective_weights": result["effective_weights"]} for result in ranked]
                metrics = retrieval_metrics(rankings, qrels)
                failures = []
                for query_id, ranking in rankings.items():
                    relevant = set(qrels[str(query_id)]["relevant"])
                    actual_rank = next((i for i, candidate_id in enumerate(ranking, 1) if candidate_id in relevant), None)
                    if actual_rank != 1:
                        failures.append({"query_id": query_id, "relevant_ids": sorted(relevant),
                                         "relevant_rank": actual_rank, "top_ids": ranking[:5],
                                         "challenge_tags": qrels[str(query_id)].get("challenge_tags", [])})
                record.update(status="ok", metrics=metrics, challenge_metrics=challenge_metrics(rankings, qrels),
                              latency_ms={"average": statistics.fmean(latencies), "median": statistics.median(latencies),
                                          "p95": percentile(latencies, .95), "samples": len(latencies),
                                          "mode": "warm_model_and_embedding_cache"},
                              failures_at_1=failures, predictions=predictions)
                print({**metrics, "avg_latency_ms": record["latency_ms"]["average"]}, flush=True)
            except Exception as exc:
                record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
                print(record["error"], flush=True)
            results.append(record)
    return {
        "benchmark": root.name, "split": split, "created_at": datetime.now(timezone.utc).isoformat(),
        "latency_note": "Warm-model, warm content-addressed embedding-cache latency around rank_reports only; machine-specific.",
        "reports_sha256": digest(split_dir / "reports.json"), "qrels_sha256": digest(split_dir / "qrels.json"),
        "image_sha256": {str(path.relative_to(split_dir)).replace('\\', '/'): digest(path) for path in sorted((split_dir / "images").glob("*"))},
        "python": platform.python_version(), "models": {"text": TEXT_MODEL, "image": IMAGE_MODEL}, "weights": WEIGHTS,
        "packages": {name: package_version(name) for name in ("sentence-transformers", "transformers", "torch", "numpy")},
        "limitations": "Synthetic development data only; no final test split and no real photos. Do not report as real-world performance.",
        "results": results,
    }


def write_results(artifact: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    lines = ["# campus_v1 development results", "", artifact["limitations"], "", artifact["latency_note"], "",
             "| Cohort | Method | Queries | Candidates | Recall@1 | Recall@3 | Recall@5 | MRR | Avg latency (ms) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in artifact["results"]:
        if row["status"] == "ok":
            m = row["metrics"]
            lines.append(f"| {row['cohort']} | {row['method']} | {row['queries']} | {row['candidates']} | {m['Recall@1']:.3f} | {m['Recall@3']:.3f} | {m['Recall@5']:.3f} | {m['MRR']:.3f} | {row['latency_ms']['average']:.2f} |")
        else:
            lines.append(f"| {row['cohort']} | {row['method']} | {row['queries']} | {row['candidates']} | failed | failed | failed | failed | failed |")
    lines.extend(["", "## Results by challenge tag", "",
                  "| Cohort | Method | Challenge | Queries | Recall@1 | Recall@3 | Recall@5 | MRR |",
                  "|---|---|---|---:|---:|---:|---:|---:|"])
    for row in artifact["results"]:
        if row["status"] != "ok":
            continue
        for tag, metrics in row["challenge_metrics"].items():
            lines.append(f"| {row['cohort']} | {row['method']} | `{tag}` | {metrics['queries']} | "
                         f"{metrics['Recall@1']:.3f} | {metrics['Recall@3']:.3f} | "
                         f"{metrics['Recall@5']:.3f} | {metrics['MRR']:.3f} |")
    lines.extend(["", "## Notable Recall@1 failures", ""])
    for row in artifact["results"]:
        if row["status"] == "ok" and row["cohort"] == "all_reports":
            lines.append(f"- **{row['method']}**: {len(row['failures_at_1'])} of {row['queries']} queries missed at rank 1. See `results.json` for IDs, ranks and tags.")
            for failure in row["failures_at_1"][:5]:
                lines.append(f"  - Query {failure['query_id']}: top candidate {failure['top_ids'][0]}; "
                             f"relevant {failure['relevant_ids'][0]} ranked {failure['relevant_rank']} "
                             f"(`{', '.join(failure['challenge_tags'])}`).")
    (output / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "data" / "benchmark" / "campus_v1")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--methods", nargs="+", choices=METHODS, default=METHODS)
    args = parser.parse_args()
    if args.split == "test" and not (args.benchmark / "test" / "reports.json").exists():
        raise SystemExit("Final test split has not been generated. Evaluate dev only at this stage.")
    artifact = evaluate(args.benchmark, args.split, args.methods)
    write_results(artifact, ROOT / "data" / "evaluation" / args.benchmark.name / args.split)
    if any(row["status"] != "ok" for row in artifact["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
