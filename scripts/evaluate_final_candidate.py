"""One-time evaluation of the precommitted candidate on frozen campus_v1/test."""
import hashlib
import json
import statistics
import time
from pathlib import Path

from src.config import ROOT
from src.matching import combine_scores
from scripts.tune_multimodal_weights import (BENCHMARK, FIELDS, IMAGE_CANDIDATE, OUTPUT as TUNING_OUTPUT,
                                               TEXT_CANDIDATE, build_signals, retrieval_metrics)

FINAL_DIR = ROOT / "data" / "evaluation" / "campus_v1" / "final"
FROZEN_CONFIG = FINAL_DIR / "frozen_config.json"
RESULTS = FINAL_DIR / "results.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[round((len(values) - 1) * fraction)]


def verify_freeze() -> tuple[dict, dict]:
    config = json.loads(FROZEN_CONFIG.read_text())
    manifest = json.loads((BENCHMARK / "test" / "manifest.json").read_text())
    if config["status"] != "frozen_before_test_generation" or config["text_model"] != TEXT_CANDIDATE or config["image_model"] != IMAGE_CANDIDATE:
        raise ValueError("Final candidate does not match the frozen model commitment")
    if manifest["status"] != "frozen" or manifest["seed"] != 9107:
        raise ValueError("Test split is not the frozen seed-9107 split")
    test_dir = BENCHMARK / "test"
    if sha256(test_dir / "reports.json") != manifest["reports_sha256"] or sha256(test_dir / "qrels.json") != manifest["qrels_sha256"]:
        raise ValueError("Frozen test reports or qrels changed")
    actual_images = {path.name: sha256(path) for path in sorted((test_dir / "images").glob("*.png"))}
    if actual_images != manifest["image_sha256"]:
        raise ValueError("Frozen test images changed")
    return config, manifest


def main() -> None:
    if RESULTS.exists():
        raise SystemExit("Final results already exist; refusing to rerun the held-out evaluation.")
    config, manifest = verify_freeze()
    queries, candidates, qrels, signals, embedding_timings = build_signals("test")
    weights = config["weights"]
    rankings, scored, latencies = {}, {}, []
    # One untimed pass warms Python and allocation paths without changing any signal.
    for query in queries[:1]:
        sorted((combine_scores(signals[(query.id, candidate.id)], weights)[0], candidate.id) for candidate in candidates)
    for query in queries:
        started = time.perf_counter()
        rows = []
        for candidate in candidates:
            score, effective = combine_scores(signals[(query.id, candidate.id)], weights)
            rows.append((candidate.id, score, effective))
        rows.sort(key=lambda row: (-row[1], row[0]))
        latencies.append((time.perf_counter() - started) * 1000)
        rankings[query.id] = [row[0] for row in rows]; scored[query.id] = rows
    metrics = retrieval_metrics(rankings, qrels)
    tags = sorted({tag for query_id in rankings for tag in qrels[str(query_id)]["challenge_tags"]})
    challenge_metrics = {}
    for tag in tags:
        subset = {query_id: ranking for query_id, ranking in rankings.items() if tag in qrels[str(query_id)]["challenge_tags"]}
        challenge_metrics[tag] = {"queries": len(subset), **retrieval_metrics(subset, qrels)}
    by_id = {item.id: item for item in queries + candidates}; failures = []
    for query in queries:
        relevant_id = qrels[str(query.id)]["relevant"][0]; ranking = rankings[query.id]; rank = ranking.index(relevant_id) + 1
        if rank != 1:
            top_id = ranking[0]
            top = next(row for row in scored[query.id] if row[0] == top_id)
            relevant = next(row for row in scored[query.id] if row[0] == relevant_id)
            failures.append({"query_id": query.id, "query_name": query.name, "query_description": query.description,
                             "top_id": top_id, "top_description": by_id[top_id].description,
                             "relevant_id": relevant_id, "relevant_description": by_id[relevant_id].description,
                             "relevant_rank": rank, "top_score": top[1], "relevant_score": relevant[1],
                             "top_components": signals[(query.id, top_id)], "relevant_components": signals[(query.id, relevant_id)],
                             "top_effective_weights": top[2], "relevant_effective_weights": relevant[2],
                             "challenge_tags": qrels[str(query.id)]["challenge_tags"]})
    result = {"status": "final_frozen_evaluation_complete", "post_test_tuning_permitted": False,
              "frozen_config_sha256": sha256(FROZEN_CONFIG), "test_manifest_sha256": sha256(BENCHMARK / "test" / "manifest.json"),
              "test_reports_sha256": manifest["reports_sha256"], "test_qrels_sha256": manifest["qrels_sha256"],
              "text_model": TEXT_CANDIDATE, "image_model": IMAGE_CANDIDATE, "weights": weights,
              "retrieval": config["retrieval"], "eligible_queries": len(queries), "candidate_count": len(candidates),
              "metrics": metrics, "challenge_metrics": challenge_metrics, "failure_count": len(failures), "failures": failures,
              "latency_ms": {"average": statistics.fmean(latencies), "median": statistics.median(latencies),
                             "p95": percentile(latencies, .95), "samples": len(latencies),
                             "mode": "warm in-memory signal combination and exhaustive sorting"},
              "embedding_generation": embedding_timings,
              "development_metrics": {"Recall@1": .9583333333333334, "Recall@3": 1., "Recall@5": 1., "MRR": .9791666666666666}}
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Frozen campus_v1 held-out evaluation", "",
             "The frozen E5 + SigLIP system was evaluated once on 16 held-out synthetic campus queries. This is not real-world accuracy.", "",
             "| Metric | Development | Final test |", "|---|---:|---:|"]
    for key in ("Recall@1", "Recall@3", "Recall@5", "MRR"):
        lines.append(f"| {key} | {result['development_metrics'][key]:.3f} | {metrics[key]:.3f} |")
    l = result["latency_ms"]
    lines += ["", f"Eligible queries: {len(queries)}. Candidates: {len(candidates)}. Top-1 failures: {len(failures)}. "
              f"Warm ranking latency: average {l['average']:.3f} ms, median {l['median']:.3f} ms, p95 {l['p95']:.3f} ms.", "",
              "## Descriptive challenge slices", "",
              "| Challenge | Queries | Recall@1 | Recall@3 | Recall@5 | MRR |", "|---|---:|---:|---:|---:|---:|"]
    for tag, row in challenge_metrics.items():
        lines.append(f"| `{tag}` | {row['queries']} | {row['Recall@1']:.3f} | {row['Recall@3']:.3f} | {row['Recall@5']:.3f} | {row['MRR']:.3f} |")
    (FINAL_DIR / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    failure_lines = ["# Frozen test failure analysis", "", "Documentation only. No post-test tuning or rerun is permitted.", ""]
    if not failures:
        failure_lines.append("No top-1 failures.")
    for failure in failures:
        failure_lines += [f"## Query {failure['query_id']}: {failure['query_name']}", "",
                          f"Correct report ranked {failure['relevant_rank']}; wrong top report {failure['top_id']}.", "",
                          f"- Query: {failure['query_description']}", f"- Wrong top: {failure['top_description']}",
                          f"- Correct: {failure['relevant_description']}",
                          f"- Scores: wrong {failure['top_score']:.4f}; correct {failure['relevant_score']:.4f}",
                          f"- Wrong components: `{failure['top_components']}`", f"- Correct components: `{failure['relevant_components']}`", ""]
    (FINAL_DIR / "failures.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": metrics, "failure_count": len(failures), "latency_ms": result["latency_ms"]}, indent=2))


if __name__ == "__main__":
    main()
