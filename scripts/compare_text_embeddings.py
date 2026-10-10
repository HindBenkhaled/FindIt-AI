"""Compare text encoders without changing production configuration or ranking code."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MODELS = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "bge-base": "BAAI/bge-base-en-v1.5",
    "e5-base": "intfloat/e5-base-v2",
}
METHODS = ["text", "full"]


def worker(model: str, benchmark: Path, output: Path) -> None:
    # Imports must happen after FINDIT_TEXT_MODEL is set by the parent process.
    from scripts.evaluate_benchmark import evaluate

    artifact = evaluate(benchmark, "dev", METHODS)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


def metric_delta(current: dict, baseline: dict) -> dict[str, float]:
    return {name: current[name] - baseline[name] for name in ("Recall@1", "Recall@3", "Recall@5", "MRR")}


def aggregate(artifacts: dict[str, dict]) -> dict:
    first = artifacts["minilm"]
    for name, artifact in artifacts.items():
        if artifact["reports_sha256"] != first["reports_sha256"] or artifact["qrels_sha256"] != first["qrels_sha256"]:
            raise ValueError(f"{name} used a different benchmark split")
        if artifact["weights"] != first["weights"] or artifact["models"]["image"] != first["models"]["image"]:
            raise ValueError(f"{name} changed image model or ranking weights")
        if any(row["status"] != "ok" for row in artifact["results"]):
            raise RuntimeError(f"{name} contains a failed evaluation method")

    baseline_rows = {(row["cohort"], row["method"]): row for row in first["results"]}
    comparisons = []
    for name, artifact in artifacts.items():
        for row in artifact["results"]:
            key = (row["cohort"], row["method"])
            baseline = baseline_rows[key]
            tag_deltas = {}
            for tag, metrics in row["challenge_metrics"].items():
                tag_deltas[tag] = metric_delta(metrics, baseline["challenge_metrics"][tag])
            comparisons.append({
                "model_key": name,
                "model": MODELS[name],
                "cohort": row["cohort"],
                "method": row["method"],
                "queries": row["queries"],
                "candidates": row["candidates"],
                "metrics": row["metrics"],
                "latency_ms": row["latency_ms"],
                "metric_delta_vs_minilm": metric_delta(row["metrics"], baseline["metrics"]),
                "challenge_metrics": row["challenge_metrics"],
                "challenge_delta_vs_minilm": tag_deltas,
                "failures_at_1": row["failures_at_1"],
            })
    return {
        "experiment": "campus_v1_text_embedding_comparison",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "split": "dev",
        "models": MODELS,
        "methods": METHODS,
        "reports_sha256": first["reports_sha256"],
        "qrels_sha256": first["qrels_sha256"],
        "image_model": first["models"]["image"],
        "weights": first["weights"],
        "latency_note": first["latency_note"],
        "protocol": "Raw drop-in text encoders; identical report text, candidates, rank_reports pipeline, image model and weights. No E5/BGE-specific prefixes.",
        "comparisons": comparisons,
    }


def write_markdown(result: dict, path: Path) -> None:
    lines = [
        "# campus_v1 text-embedding comparison",
        "",
        result["protocol"],
        "",
        result["latency_note"],
        "",
        "## Overall results",
        "",
        "| Cohort | Method | Encoder | Queries | Candidates | Recall@1 | Recall@3 | Recall@5 | MRR | Avg ms | Median ms | P95 ms |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["comparisons"]:
        metrics, latency = row["metrics"], row["latency_ms"]
        lines.append(
            f"| {row['cohort']} | {row['method']} | {row['model_key']} | {row['queries']} | {row['candidates']} | "
            f"{metrics['Recall@1']:.3f} | {metrics['Recall@3']:.3f} | {metrics['Recall@5']:.3f} | {metrics['MRR']:.3f} | "
            f"{latency['average']:.2f} | {latency['median']:.2f} | {latency['p95']:.2f} |"
        )
    lines.extend([
        "",
        "## Challenge-tag changes versus MiniLM",
        "",
        "Positive values improved and negative values worsened. Zero means unchanged.",
        "",
        "| Cohort | Method | Encoder | Challenge | Queries | Recall@1 | Δ Recall@1 | MRR | Δ MRR |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in result["comparisons"]:
        for tag, metrics in row["challenge_metrics"].items():
            delta = row["challenge_delta_vs_minilm"][tag]
            lines.append(
                f"| {row['cohort']} | {row['method']} | {row['model_key']} | `{tag}` | {metrics['queries']} | "
                f"{metrics['Recall@1']:.3f} | {delta['Recall@1']:+.3f} | {metrics['MRR']:.3f} | {delta['MRR']:+.3f} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=Path("data/benchmark/campus_v1"))
    parser.add_argument("--output", type=Path, default=Path("data/evaluation/campus_v1/text_embedding_comparison"))
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--model", choices=MODELS, help=argparse.SUPPRESS)
    parser.add_argument("--worker-output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if not args.model or not args.worker_output:
            parser.error("worker requires --model and --worker-output")
        worker(args.model, args.benchmark, args.worker_output)
        return

    args.output.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, model in MODELS.items():
        raw_path = args.output / f"{name}.json"
        env = os.environ.copy()
        env["FINDIT_TEXT_MODEL"] = model
        command = [sys.executable, "-m", "scripts.compare_text_embeddings", "--worker", "--model", name,
                   "--benchmark", str(args.benchmark), "--worker-output", str(raw_path)]
        print(f"Evaluating {name}: {model}", flush=True)
        subprocess.run(command, check=True, env=env)
        artifacts[name] = json.loads(raw_path.read_text(encoding="utf-8"))
    result = aggregate(artifacts)
    (args.output / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_markdown(result, args.output / "results.md")


if __name__ == "__main__":
    main()
