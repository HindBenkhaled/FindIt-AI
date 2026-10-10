import json
from pathlib import Path

import pytest

from src.image_benchmark import load_protocol, validate_protocol


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "data" / "benchmark" / "image_retrieval" / "coil100_v1"


@pytest.mark.parametrize("setting", ["easy", "hard"])
def test_coil100_protocol_is_complete_and_exact_object(setting):
    queries, gallery, qrels, digest = load_protocol(BENCHMARK, setting)
    assert len(queries) == len(gallery) == len(qrels) == 200
    assert len(digest) == 64
    assert not ({item["id"] for item in queries} & {item["id"] for item in gallery})
    assert all(len(labels["relevant"]) == 2 for labels in qrels.values())


def test_cross_object_relevance_is_rejected():
    queries, gallery, qrels, _ = load_protocol(BENCHMARK, "easy")
    broken = json.loads(json.dumps(qrels))
    broken[queries[0]["id"]]["relevant"] = [gallery[-1]["id"]]
    with pytest.raises(ValueError, match="Cross-object"):
        validate_protocol(queries, gallery, broken)


def test_model_outputs_are_isolated():
    root = ROOT / "data" / "evaluation" / "image_retrieval" / "coil100_v1"
    paths = [root / model / "results.json" for model in ("clip", "siglip", "dinov2")]
    assert len({path.resolve() for path in paths}) == 3
    assert all(path.is_file() for path in paths)
