"""Tune balanced multimodal weights on campus_v1 development data only."""
import argparse
import importlib.metadata
import itertools
import json
import platform
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from src.benchmark import load_split
from src.config import DEVICE, IMAGE_MODEL, ROOT, TEXT_MODEL, WEIGHTS
from src.matching import category_similarity, combine_scores, cosine_similarity, location_similarity, time_similarity
from src.services import report_text

TEXT_CANDIDATE = "intfloat/e5-base-v2"
IMAGE_CANDIDATE = "google/siglip-base-patch16-224"
BENCHMARK = ROOT / "data" / "benchmark" / "campus_v1"
TUNING_SPLIT = "dev"
OUTPUT = ROOT / "data" / "evaluation" / "campus_v1" / "weight_tuning"
FIELDS = ("text", "image", "location", "time", "category")
RANGES = {"text": (20, 50), "image": (20, 50), "location": (5, 20), "time": (5, 15), "category": (5, 15)}


def candidate_weights() -> list[dict[str, float]]:
    values = {key: range(low, high + 1, 5) for key, (low, high) in RANGES.items()}
    combinations = []
    for raw in itertools.product(*(values[key] for key in FIELDS)):
        if sum(raw) == 100:
            combinations.append({key: value / 100 for key, value in zip(FIELDS, raw)})
    return combinations


def validate_weights(weights: dict[str, float]) -> None:
    if set(weights) != set(FIELDS) or any(value < 0 for value in weights.values()):
        raise ValueError("Weights must contain five non-negative signals")
    if not np.isclose(sum(weights.values()), 1.0):
        raise ValueError("Weights must sum to 1.0")


def encode_texts(texts: list[str]) -> np.ndarray:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(TEXT_CANDIDATE, device=DEVICE, trust_remote_code=False)
    return np.asarray(model.encode(texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False), dtype=np.float32)


def encode_images(paths: list[Path]) -> np.ndarray:
    import torch
    from transformers import AutoImageProcessor, AutoModel
    processor = AutoImageProcessor.from_pretrained(IMAGE_CANDIDATE, trust_remote_code=False)
    model = AutoModel.from_pretrained(IMAGE_CANDIDATE, trust_remote_code=False).to(DEVICE).eval()
    vectors = []
    for start in range(0, len(paths), 16):
        images = []
        for path in paths[start:start + 16]:
            with Image.open(path) as source:
                images.append(source.convert("RGB"))
        inputs = {key: value.to(DEVICE) for key, value in processor(images=images, return_tensors="pt").items()}
        with torch.inference_mode():
            output = model.get_image_features(**inputs)
            output = torch.nn.functional.normalize(output, dim=-1)
        vectors.append(output.cpu().numpy().astype(np.float32))
    return np.concatenate(vectors)


def build_signals(split: str = TUNING_SPLIT) -> tuple[list, list, dict, dict, dict]:
    if split not in {"dev", "test"}:
        raise ValueError("Unknown benchmark split")
    if TUNING_SPLIT != "dev":
        raise RuntimeError("Weight tuning may load development data only")
    reports, qrels = load_split(BENCHMARK, split)
    queries = [item for item in reports if item.report_type == "lost"]
    candidates = [item for item in reports if item.report_type == "found"]
    texts = [report_text(item) for item in reports]
    started = time.perf_counter(); text_vectors = encode_texts(texts); text_seconds = time.perf_counter() - started
    text_by_id = {item.id: text_vectors[index] for index, item in enumerate(reports)}
    image_reports = [item for item in reports if item.image_path]
    started = time.perf_counter()
    image_vectors = encode_images([BENCHMARK / split / item.image_path for item in image_reports])
    image_seconds = time.perf_counter() - started
    image_by_id = {item.id: image_vectors[index] for index, item in enumerate(image_reports)}
    signals = {}
    for query in queries:
        for candidate in candidates:
            signals[(query.id, candidate.id)] = {
                "text": cosine_similarity(text_by_id[query.id], text_by_id[candidate.id]),
                "image": cosine_similarity(image_by_id[query.id], image_by_id[candidate.id])
                         if query.id in image_by_id and candidate.id in image_by_id else None,
                "location": location_similarity(query.location, candidate.location),
                "time": time_similarity(query.event_date, candidate.event_date),
                "category": category_similarity(query.category, candidate.category),
            }
    timings = {"text_embedding_seconds": text_seconds, "image_embedding_seconds": image_seconds,
               "reports": len(reports), "images": len(image_reports)}
    return queries, candidates, qrels, signals, timings


def retrieval_metrics(rankings: dict[int, list[int]], qrels: dict) -> dict[str, float]:
    totals = {"Recall@1": 0., "Recall@3": 0., "Recall@5": 0., "MRR": 0.}
    for query_id, ranked in rankings.items():
        relevant = set(qrels[str(query_id)]["relevant"])
        for k in (1, 3, 5):
            totals[f"Recall@{k}"] += len(set(ranked[:k]) & relevant) / len(relevant)
        rank = next((index for index, item in enumerate(ranked, 1) if item in relevant), None)
        totals["MRR"] += 1 / rank if rank else 0
    return {key: value / len(rankings) for key, value in totals.items()}


def evaluate_weights(weights: dict[str, float], queries: list, candidates: list, qrels: dict, signals: dict) -> dict:
    validate_weights(weights)
    rankings, scored = {}, {}
    for query in queries:
        rows = []
        for candidate in candidates:
            score, effective = combine_scores(signals[(query.id, candidate.id)], weights)
            rows.append((candidate.id, score, effective))
        rows.sort(key=lambda row: (-row[1], row[0]))
        rankings[query.id] = [row[0] for row in rows]
        scored[query.id] = rows
    metrics = retrieval_metrics(rankings, qrels)
    tags = sorted({tag for query_id in rankings for tag in qrels[str(query_id)]["challenge_tags"]})
    tag_metrics = {}
    for tag in tags:
        subset = {query_id: ranking for query_id, ranking in rankings.items()
                  if tag in qrels[str(query_id)]["challenge_tags"]}
        tag_metrics[tag] = {"queries": len(subset), **retrieval_metrics(subset, qrels)}
    failures = []
    by_id = {item.id: item for item in queries + candidates}
    for query_id, ranking in rankings.items():
        relevant_id = qrels[str(query_id)]["relevant"][0]
        rank = ranking.index(relevant_id) + 1
        if rank != 1:
            top_id = ranking[0]
            top_row = next(row for row in scored[query_id] if row[0] == top_id)
            relevant_row = next(row for row in scored[query_id] if row[0] == relevant_id)
            failures.append({"query_id": query_id, "query_name": by_id[query_id].name,
                             "top_id": top_id, "top_name": by_id[top_id].name,
                             "relevant_id": relevant_id, "relevant_name": by_id[relevant_id].name,
                             "relevant_rank": rank, "challenge_tags": qrels[str(query_id)]["challenge_tags"],
                             "top_components": signals[(query_id, top_id)], "relevant_components": signals[(query_id, relevant_id)],
                             "top_score": top_row[1], "relevant_score": relevant_row[1],
                             "top_effective_weights": top_row[2], "relevant_effective_weights": relevant_row[2]})
    return {"weights": weights, "metrics": metrics, "challenge_metrics": tag_metrics,
            "failure_count": len(failures), "failures": failures}


def robustness(candidate: dict, baseline: dict) -> dict:
    changes, substantial = {}, []
    for tag, current in candidate["challenge_metrics"].items():
        base = baseline["challenge_metrics"][tag]
        delta = {"Recall@1": current["Recall@1"] - base["Recall@1"], "MRR": current["MRR"] - base["MRR"]}
        changes[tag] = delta
        if delta["Recall@1"] < -.25 or delta["MRR"] < -.125:
            substantial.append(tag)
    return {"tag_changes_vs_baseline": changes, "substantially_worsened_tags": substantial,
            "max_weight": max(candidate["weights"].values()),
            "l1_distance_from_current": sum(abs(candidate["weights"][key] - WEIGHTS[key]) for key in FIELDS)}


def compact(result: dict) -> dict:
    return {key: result[key] for key in ("weights", "metrics", "challenge_metrics", "failure_count")}


def write_markdown(baseline: dict, ranked: list[dict], selected: dict, combinations: int) -> None:
    lines = ["# campus_v1 candidate-stack weight tuning", "",
             f"Development-only constrained grid: {combinations} combinations. Text `{TEXT_CANDIDATE}`; image `{IMAGE_CANDIDATE}`.", "",
             "| Candidate | Text | Image | Location | Time | Category | Recall@1 | MRR | Failures | Worsened tags |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    rows = [("Current weights", baseline)] + [(f"Top {index}", item) for index, item in enumerate(ranked[:10], 1)]
    for label, row in rows:
        w, m = row["weights"], row["metrics"]
        worsened = ", ".join(row.get("robustness", {}).get("substantially_worsened_tags", [])) or "none"
        lines.append(f"| {label} | {w['text']:.2f} | {w['image']:.2f} | {w['location']:.2f} | {w['time']:.2f} | {w['category']:.2f} | {m['Recall@1']:.3f} | {m['MRR']:.3f} | {row['failure_count']} | {worsened} |")
    lines += ["", "## Selected balanced candidate", "", f"`{json.dumps(selected['weights'], sort_keys=True)}`", "",
              f"Recall@1 {selected['metrics']['Recall@1']:.3f}; MRR {selected['metrics']['MRR']:.3f}; {selected['failure_count']} top-1 failures.", "",
              "## Per-tag baseline versus selected", "",
              "| Challenge | Queries | Baseline R@1 | Selected R@1 | Baseline MRR | Selected MRR |",
              "|---|---:|---:|---:|---:|---:|"]
    for tag, current in selected["challenge_metrics"].items():
        base = baseline["challenge_metrics"][tag]
        lines.append(f"| `{tag}` | {current['queries']} | {base['Recall@1']:.3f} | {current['Recall@1']:.3f} | {base['MRR']:.3f} | {current['MRR']:.3f} |")
    lines += ["", "## Remaining selected-candidate failures", ""]
    for failure in selected["failures"]:
        lines.append(f"- Query {failure['query_id']} ({failure['query_name']}): ranked {failure['top_id']} first instead of {failure['relevant_id']} (relevant rank {failure['relevant_rank']}); tags `{', '.join(failure['challenge_tags'])}`.")
        lines.append(f"  The top candidate scored {failure['top_score']:.4f} versus {failure['relevant_score']:.4f}. "
                     f"Components (top / relevant): text {failure['top_components']['text']:.4f} / {failure['relevant_components']['text']:.4f}, "
                     f"image {failure['top_components']['image']} / {failure['relevant_components']['image']}, "
                     f"location {failure['top_components']['location']:.4f} / {failure['relevant_components']['location']:.4f}, "
                     f"time {failure['top_components']['time']:.4f} / {failure['relevant_components']['time']:.4f}, "
                     f"category {failure['top_components']['category']:.4f} / {failure['relevant_components']['category']:.4f}.")
    lines += ["", "The scratch/mark, backpack, location-conflict, date-gap, and single-missing-image cases are correct at rank 1 under both the untuned baseline and selected candidate. The remaining umbrella has no image on either side; all contextual components tie, so its slightly higher wrong-candidate text similarity decides the order."]
    (OUTPUT / "top_candidates.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse-signals", action="store_true", help="Reuse the experiment signal cache if present")
    args = parser.parse_args(); OUTPUT.mkdir(parents=True, exist_ok=True)
    cache_path = OUTPUT / "signals.json"
    if args.reuse_signals and cache_path.exists():
        cached = json.loads(cache_path.read_text())
        if cached.get("split") != TUNING_SPLIT or cached.get("text_model") != TEXT_CANDIDATE or cached.get("image_model") != IMAGE_CANDIDATE:
            raise ValueError("Signal cache does not match the controlled development experiment")
        reports, qrels = load_split(BENCHMARK, TUNING_SPLIT)
        queries = [item for item in reports if item.report_type == "lost"]; candidates = [item for item in reports if item.report_type == "found"]
        signals = {(int(q), int(c)): values for q, candidates_map in cached["signals"].items() for c, values in candidates_map.items()}
        timings = cached["timings"]
    else:
        queries, candidates, qrels, signals, timings = build_signals()
        serialized = {str(q.id): {str(c.id): signals[(q.id, c.id)] for c in candidates} for q in queries}
        cache_path.write_text(json.dumps({"text_model": TEXT_CANDIDATE, "image_model": IMAGE_CANDIDATE,
                                          "split": TUNING_SPLIT, "timings": timings, "signals": serialized}, indent=2), encoding="utf-8")
    baseline = evaluate_weights(dict(WEIGHTS), queries, candidates, qrels, signals)
    grid = []
    for weights in candidate_weights():
        result = evaluate_weights(weights, queries, candidates, qrels, signals)
        result["robustness"] = robustness(result, baseline); grid.append(result)
    ranked = sorted(grid, key=lambda row: (-row["metrics"]["Recall@1"], -row["metrics"]["MRR"],
                                            len(row["robustness"]["substantially_worsened_tags"]),
                                            row["robustness"]["l1_distance_from_current"], tuple(row["weights"][key] for key in FIELDS)))
    robust = [row for row in ranked if not row["robustness"]["substantially_worsened_tags"]]
    selected = robust[0] if robust else ranked[0]
    best_recall = ranked[0]
    best_mrr = sorted(grid, key=lambda row: (-row["metrics"]["MRR"], -row["metrics"]["Recall@1"], row["robustness"]["l1_distance_from_current"]))[0]
    metadata = {"created_at": datetime.now(timezone.utc).isoformat(), "split": TUNING_SPLIT, "final_test_loaded": False,
                "text_model": TEXT_CANDIDATE, "image_model": IMAGE_CANDIDATE,
                "production_models": {"text": TEXT_MODEL, "image": IMAGE_MODEL}, "production_weights": WEIGHTS,
                "ranges": RANGES, "step": .05, "combination_count": len(grid), "timings": timings,
                "packages": {name: importlib.metadata.version(name) for name in ("numpy", "torch", "transformers", "sentence-transformers")},
                "python": platform.python_version(), "device": DEVICE}
    (OUTPUT / "baseline_candidate.json").write_text(json.dumps({**metadata, **baseline}, indent=2), encoding="utf-8")
    (OUTPUT / "grid_results.json").write_text(json.dumps({**metadata, "best_recall_candidate": compact(best_recall),
                                                            "best_mrr_candidate": compact(best_mrr),
                                                            "results": [compact(row) | {"robustness": row["robustness"]} for row in grid]}, indent=2), encoding="utf-8")
    (OUTPUT / "selected_candidate.json").write_text(json.dumps({**metadata, **selected}, indent=2), encoding="utf-8")
    write_markdown(baseline, ranked, selected, len(grid))
    print(f"Evaluated {len(grid)} weight sets; selected {selected['weights']} -> {selected['metrics']}")


if __name__ == "__main__":
    main()
