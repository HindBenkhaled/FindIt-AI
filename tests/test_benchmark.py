import json

import pytest

from scripts.evaluate_benchmark import challenge_metrics, retrieval_metrics
from src.benchmark import load_split


def test_benchmark_metrics_count_misses_and_tags():
    qrels = {
        "1": {"relevant": [11], "challenge_tags": ["similar_item"]},
        "2": {"relevant": [22], "challenge_tags": ["similar_item", "date_gap"]},
    }
    rankings = {1: [11, 12], 2: [21, 22]}
    assert retrieval_metrics(rankings, qrels) == {"Recall@1": 0.5, "Recall@3": 1.0, "Recall@5": 1.0, "MRR": 0.75}
    assert challenge_metrics(rankings, qrels)["date_gap"]["MRR"] == 0.5


def test_frozen_dev_benchmark_is_valid():
    from scripts.generate_benchmark import ROOT_DIR
    reports, qrels = load_split(ROOT_DIR, "dev")
    assert len(qrels) == 24
    assert len(reports) == 72
    assert all(label["hard_negatives"] for label in qrels.values())
    assert (ROOT_DIR / "test" / "manifest.json").exists()


def test_benchmark_rejects_non_found_relevance(tmp_path):
    split = tmp_path / "dev"
    split.mkdir()
    reports = {"split": "dev", "reports": [{"id": 1, "report_type": "lost", "event_date": None, "image_path": None}]}
    qrels = {"split": "dev", "qrels": {"1": {"relevant": [1]}}}
    (split / "reports.json").write_text(json.dumps(reports))
    (split / "qrels.json").write_text(json.dumps(qrels))
    with pytest.raises(ValueError, match="found report"):
        load_split(tmp_path, "dev")
