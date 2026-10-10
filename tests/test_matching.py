from datetime import date, timedelta
from types import SimpleNamespace

import numpy as np
import pytest

from scripts.evaluate import retrieval_metrics
from src.matching import (category_similarity, combine_scores, cosine_similarity,
                          keyword_similarity, location_similarity, normalize_text, time_similarity)
from src.services import rank_reports, report_text


def report(item_id=1, kind="lost", **overrides):
    values = dict(id=item_id, report_type=kind, name="Blue bag", description="Blue backpack yellow pocket",
                  category="Bag", location="Library", event_date=date(2026, 9, 20), image_path=None)
    return SimpleNamespace(**(values | overrides))


def test_normalization():
    assert normalize_text("  BLACK—AirPods!!  Case ") == "black airpods case"
    assert normalize_text("ＣＡＳＥ") == "case"
    assert keyword_similarity("Blue BAG", "bag blue") == 1
    assert keyword_similarity("", "") == 0


def test_date_decay_and_chronology():
    day = date(2026, 9, 20)
    assert time_similarity(day, day) == 1
    assert time_similarity(day, day + timedelta(days=1)) > time_similarity(day, day + timedelta(days=30))
    assert time_similarity(day, day - timedelta(days=1)) < time_similarity(day, day + timedelta(days=1))
    assert time_similarity(None, day) is None
    with pytest.raises(ValueError):
        time_similarity(day, day, 0)


def test_category_and_location():
    assert category_similarity("Wallet", "wallet") == 1
    assert 0 < category_similarity("Wallet", "Bag") < 0.5
    assert category_similarity("Other", "Other") == 0.5
    assert category_similarity(None, "Bag") is None
    assert location_similarity(" Library ", "LIBRARY") == 1
    assert 0 < location_similarity("Library", "Second floor library") < 1
    assert location_similarity("", "Library") is None


def test_missing_components_are_renormalized():
    score, weights = combine_scores({"text": 0.8, "image": None}, {"text": 0.3, "image": 0.7})
    assert score == pytest.approx(0.8)
    assert weights == {"text": 1}
    score, weights = combine_scores({"text": 0.8, "image": 0.0}, {"text": 0.3, "image": 0.7})
    assert score == pytest.approx(0.24)  # A real zero is different from unavailable.
    assert sum(weights.values()) == pytest.approx(1)


@pytest.mark.parametrize("components,weights", [({"text": None}, {"text": 1}), ({"text": 1}, {"text": -1}),
                                                  ({"text": float("nan")}, {"text": 1}), ({"text": 1.1}, {"text": 1}),
                                                  ({"text": 0.5}, {})])
def test_invalid_scoring_inputs(components, weights):
    with pytest.raises(ValueError):
        combine_scores(components, weights)


def test_cosine():
    assert cosine_similarity(np.array([1, 0]), np.array([1, 0])) == 1
    assert cosine_similarity(np.array([1, 0]), np.array([-1, 0])) == 0
    assert cosine_similarity(np.zeros(2), np.ones(2)) == 0


def test_baseline_ranking_and_deterministic_ties():
    query = report()
    good = report(10, "found")
    duplicate = report(11, "found")
    bad = report(2, "found", name="Wallet", description="Black leather wallet", category="Wallet", location="Airport")
    ranked = rank_reports(query, [bad, duplicate, good, report(22)], "baseline")
    assert [r["item"].id for r in ranked] == [10, 11, 2]
    assert ranked[0]["components"]["image"] is None
    assert sum(ranked[0]["effective_weights"].values()) == pytest.approx(1)
    with pytest.raises(ValueError):
        rank_reports(good, [bad], "baseline")


def test_multimodal_service_with_controlled_embeddings(monkeypatch):
    from src import embeddings
    monkeypatch.setattr(embeddings, "text_embedding", lambda text: np.array([1., 0.]))
    monkeypatch.setattr(embeddings, "image_embedding", lambda path: np.array([0., 1.]))
    query = report(image_path="q.jpg")
    candidates = [report(2, "found", image_path="f.jpg"), report(3, "found")]
    ranked = rank_reports(query, candidates, "full", resolve_image=lambda name: name)
    assert len(ranked) == 2
    assert ranked[0]["score"] == pytest.approx(1)
    no_image = next(r for r in ranked if r["item"].id == 3)
    assert "image" not in no_image["effective_weights"]
    assert no_image["components"]["image"] is None
    assert len(rank_reports(query, candidates, "image", resolve_image=lambda name: name)) == 1
    with pytest.raises(ValueError, match="requires an image"):
        rank_reports(report(), candidates, "image")


def test_metrics_include_misses_and_multiple_relevant_items():
    metrics = retrieval_metrics({1: [4, 2, 3], 2: [7, 8]}, {"1": [2, 3], "2": [9]})
    assert metrics == {"Recall@1": 0, "Recall@3": 0.5, "Recall@5": 0.5, "MRR": 0.25}


def test_internal_matching_text_includes_private_fields():
    item = report(identifying_details="engraved initials HX", location_detail="under desk 14")
    assert "engraved initials HX" in report_text(item)
    assert "under desk 14" in report_text(item)
