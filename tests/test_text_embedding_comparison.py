import pytest

from scripts.compare_text_embeddings import MODELS, metric_delta


def test_metric_delta():
    baseline = {"Recall@1": .5, "Recall@3": .8, "Recall@5": 1., "MRR": .7}
    current = {"Recall@1": .75, "Recall@3": .8, "Recall@5": 1., "MRR": .8}
    assert metric_delta(current, baseline) == pytest.approx(
        {"Recall@1": .25, "Recall@3": 0., "Recall@5": 0., "MRR": .1}
    )


def test_required_models_are_declared():
    assert MODELS == {
        "minilm": "sentence-transformers/all-MiniLM-L6-v2",
        "bge-base": "BAAI/bge-base-en-v1.5",
        "e5-base": "intfloat/e5-base-v2",
    }
