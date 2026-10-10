"""Controlled NumPy brute-force versus exact FAISS vector retrieval benchmark."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import faiss
import numpy as np

from src.config import ROOT

SEED = 20261010
DIMENSION = 768
SIZES = (100, 1_000, 10_000, 50_000, 100_000)
TOP_K = 10
HNSW_M = 32
HNSW_EF_CONSTRUCTION = 80
HNSW_EF_SEARCH = 64
OUTPUT = ROOT / "data" / "evaluation" / "vector_retrieval" / "faiss_v1"


def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Cannot normalize zero vectors")
    vectors /= norms
    return vectors


def percentile(values: list[float], fraction: float) -> float:
    return sorted(values)[round((len(values) - 1) * fraction)]


def latency_summary(values: list[float]) -> dict:
    return {"average": statistics.fmean(values), "median": statistics.median(values),
            "p95": percentile(values, .95), "samples": len(values)}


def brute_search(vectors: np.ndarray, query: np.ndarray, k: int) -> np.ndarray:
    scores = vectors @ query
    # Full stable sort matches the repository's current full-scan-then-sort design.
    return np.argsort(-scores, kind="stable")[:k]


def overlap_recall(actual: np.ndarray, expected: np.ndarray, k: int) -> float:
    return len(set(actual[:k].tolist()) & set(expected[:k].tolist())) / k


def benchmark_size(vectors: np.ndarray, queries: np.ndarray) -> dict:
    for query in queries[:3]:
        brute_search(vectors, query, TOP_K)
    brute_rankings, brute_latencies = [], []
    for query in queries:
        started = time.perf_counter(); ranking = brute_search(vectors, query, TOP_K)
        brute_latencies.append((time.perf_counter() - started) * 1000); brute_rankings.append(ranking)
    brute_rankings = np.stack(brute_rankings)

    started = time.perf_counter(); index = faiss.IndexFlatIP(vectors.shape[1]); index.add(vectors)
    build_seconds = time.perf_counter() - started
    for query in queries[:3]:
        index.search(query[None, :], TOP_K)
    faiss_rankings, faiss_latencies = [], []
    for query in queries:
        started = time.perf_counter(); _, ranking = index.search(query[None, :], TOP_K)
        faiss_latencies.append((time.perf_counter() - started) * 1000); faiss_rankings.append(ranking[0])
    faiss_rankings = np.stack(faiss_rankings)
    recalls = {f"Recall@{k}": statistics.fmean(
        overlap_recall(faiss_rankings[i], brute_rankings[i], k) for i in range(len(queries))
    ) for k in (1, 5, 10)}
    exact_top10_agreement = float(np.mean(np.all(faiss_rankings == brute_rankings, axis=1)))
    started = time.perf_counter()
    hnsw = faiss.IndexHNSWFlat(vectors.shape[1], HNSW_M, faiss.METRIC_INNER_PRODUCT)
    hnsw.hnsw.efConstruction = HNSW_EF_CONSTRUCTION
    hnsw.hnsw.efSearch = HNSW_EF_SEARCH
    hnsw.add(vectors)
    hnsw_build_seconds = time.perf_counter() - started
    for query in queries[:3]:
        hnsw.search(query[None, :], TOP_K)
    hnsw_rankings, hnsw_latencies = [], []
    for query in queries:
        started = time.perf_counter(); _, ranking = hnsw.search(query[None, :], TOP_K)
        hnsw_latencies.append((time.perf_counter() - started) * 1000); hnsw_rankings.append(ranking[0])
    hnsw_rankings = np.stack(hnsw_rankings)
    hnsw_recalls = {f"Recall@{k}": statistics.fmean(
        overlap_recall(hnsw_rankings[i], brute_rankings[i], k) for i in range(len(queries))
    ) for k in (1, 5, 10)}
    # Raw vectors plus an approximate 2*M 32-bit neighbor links per vector.
    hnsw_bytes = int(vectors.nbytes + len(vectors) * 2 * HNSW_M * 4)
    return {
        "vector_count": len(vectors), "query_count": len(queries), "dimension": vectors.shape[1],
        "brute_force": {"index_build_seconds": 0.0, "latency_ms": latency_summary(brute_latencies),
                        "estimated_index_bytes": int(vectors.nbytes)},
        "faiss_index_flat_ip": {"index_build_seconds": build_seconds, "latency_ms": latency_summary(faiss_latencies),
                                "estimated_index_bytes": int(index.ntotal * index.d * 4), **recalls,
                                "exact_top10_order_agreement": exact_top10_agreement},
        "faiss_hnsw_flat": {"index_build_seconds": hnsw_build_seconds, "latency_ms": latency_summary(hnsw_latencies),
                            "estimated_index_bytes": hnsw_bytes, "M": HNSW_M,
                            "efConstruction": HNSW_EF_CONSTRUCTION, "efSearch": HNSW_EF_SEARCH, **hnsw_recalls},
    }


def actual_findit_validation() -> dict:
    from src import embeddings
    from src.benchmark import load_split
    from src.services import report_text

    reports, _ = load_split(ROOT / "data" / "benchmark" / "campus_v1", "dev")
    queries = [item for item in reports if item.report_type == "lost"]
    candidates = [item for item in reports if item.report_type == "found"]
    candidate_vectors = normalize(np.stack([embeddings.text_embedding(report_text(item)) for item in candidates]).astype(np.float32))
    query_vectors = normalize(np.stack([embeddings.text_embedding(report_text(item)) for item in queries]).astype(np.float32))
    index = faiss.IndexFlatIP(candidate_vectors.shape[1]); index.add(candidate_vectors)
    agreements, recalls = [], {1: [], 5: [], 10: []}
    failures = []
    for query, vector in zip(queries, query_vectors):
        brute = brute_search(candidate_vectors, vector, TOP_K)
        _, found = index.search(vector[None, :], TOP_K); found = found[0]
        agreements.append(np.array_equal(brute, found))
        for k in recalls:
            recalls[k].append(overlap_recall(found, brute, k))
        if not np.array_equal(brute, found):
            failures.append({"query_id": query.id, "brute_ids": [candidates[i].id for i in brute],
                             "faiss_ids": [candidates[i].id for i in found]})
    return {"model_id": embeddings.TEXT_MODEL, "query_count": len(queries), "candidate_count": len(candidates),
            "dimension": int(candidate_vectors.shape[1]), "Recall@1": statistics.fmean(recalls[1]),
            "Recall@5": statistics.fmean(recalls[5]), "Recall@10": statistics.fmean(recalls[10]),
            "exact_top10_order_agreement": statistics.fmean(agreements), "failures": failures}


def write_results(result: dict) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# FAISS scalability benchmark", "", result["scope"], "",
             "| Vectors | Method | Recall@1 | Recall@5 | Recall@10 | Avg ms | Median ms | P95 ms | Build ms | Approx memory MiB |",
             "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in result["synthetic_results"]:
        brute, exact = row["brute_force"], row["faiss_index_flat_ip"]
        lines.append(f"| {row['vector_count']:,} | NumPy brute force | ground truth | ground truth | ground truth | "
                     f"{brute['latency_ms']['average']:.3f} | {brute['latency_ms']['median']:.3f} | {brute['latency_ms']['p95']:.3f} | 0.000 | {brute['estimated_index_bytes']/2**20:.2f} |")
        lines.append(f"| {row['vector_count']:,} | FAISS IndexFlatIP | {exact['Recall@1']:.3f} | {exact['Recall@5']:.3f} | {exact['Recall@10']:.3f} | "
                     f"{exact['latency_ms']['average']:.3f} | {exact['latency_ms']['median']:.3f} | {exact['latency_ms']['p95']:.3f} | "
                     f"{exact['index_build_seconds']*1000:.3f} | {exact['estimated_index_bytes']/2**20:.2f} |")
        hnsw = row["faiss_hnsw_flat"]
        lines.append(f"| {row['vector_count']:,} | FAISS HNSWFlat | {hnsw['Recall@1']:.3f} | {hnsw['Recall@5']:.3f} | {hnsw['Recall@10']:.3f} | "
                     f"{hnsw['latency_ms']['average']:.3f} | {hnsw['latency_ms']['median']:.3f} | {hnsw['latency_ms']['p95']:.3f} | "
                     f"{hnsw['index_build_seconds']*1000:.3f} | {hnsw['estimated_index_bytes']/2**20:.2f} |")
    integration = result["findit_integration"]
    lines += ["", "## Actual FindIt embedding validation", "",
              f"Current `{integration['model_id']}` embeddings: {integration['query_count']} queries, "
              f"{integration['candidate_count']} candidates, {integration['dimension']} dimensions.", "",
              f"FAISS versus brute force: Recall@1 {integration['Recall@1']:.3f}, Recall@5 {integration['Recall@5']:.3f}, "
              f"Recall@10 {integration['Recall@10']:.3f}, exact top-10 order agreement {integration['exact_top10_order_agreement']:.3f}.", "",
              f"`IndexFlatIP` is exact over normalized float32 vectors. HNSW uses M={HNSW_M}, "
              f"efConstruction={HNSW_EF_CONSTRUCTION}, and efSearch={HNSW_EF_SEARCH}."]
    (OUTPUT / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=int, default=50)
    parser.add_argument("--sizes", type=int, nargs="+", default=SIZES)
    args = parser.parse_args()
    if min(args.sizes) < TOP_K or args.queries < 1:
        parser.error("sizes must be at least 10 and queries must be positive")
    rng = np.random.default_rng(SEED)
    started = time.perf_counter(); vectors = normalize(rng.standard_normal((max(args.sizes), DIMENSION), dtype=np.float32)); queries = normalize(rng.standard_normal((args.queries, DIMENSION), dtype=np.float32)); generation_seconds = time.perf_counter() - started
    rows = []
    for size in args.sizes:
        print(f"Benchmarking {size:,} vectors", flush=True); rows.append(benchmark_size(np.ascontiguousarray(vectors[:size]), queries))
    result = {"benchmark": "faiss_v1", "created_at": datetime.now(timezone.utc).isoformat(), "seed": SEED,
              "dimension": DIMENSION, "dtype": "float32", "normalization": "L2", "query_count": args.queries,
              "vector_sha256": hashlib.sha256(vectors.tobytes()).hexdigest(),
              "query_sha256": hashlib.sha256(queries.tobytes()).hexdigest(),
              "vector_generation_seconds": generation_seconds, "scope": "Vector search only; model inference, multimodal scoring and model loading are excluded.",
              "methods": ["NumPy matrix-vector dot plus stable full argsort", "faiss.IndexFlatIP",
                          f"faiss.IndexHNSWFlat(M={HNSW_M}, efConstruction={HNSW_EF_CONSTRUCTION}, efSearch={HNSW_EF_SEARCH})"],
              "faiss_threads": faiss.omp_get_max_threads(), "cpu_count": os.cpu_count(), "python": platform.python_version(),
              "packages": {name: importlib.metadata.version(name) for name in ("numpy", "faiss-cpu")},
              "synthetic_results": rows, "findit_integration": actual_findit_validation()}
    write_results(result)


if __name__ == "__main__":
    main()
