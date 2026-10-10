import pytest

from scripts.tune_multimodal_weights import (FIELDS, IMAGE_CANDIDATE, TEXT_CANDIDATE, TUNING_SPLIT,
                                               candidate_weights, validate_weights)
from src.matching import combine_scores
from src.config import IMAGE_MODEL, TEXT_MODEL, WEIGHTS


def test_candidate_grid_is_bounded_and_normalized():
    candidates = candidate_weights()
    assert candidates
    assert len({tuple(row[key] for key in FIELDS) for row in candidates}) == len(candidates)
    for weights in candidates:
        validate_weights(weights)
        assert all(0 <= value <= .5 for value in weights.values())


def test_invalid_weights_are_rejected():
    with pytest.raises(ValueError):
        validate_weights({"text": 1., "image": -.1, "location": .05, "time": .025, "category": .025})


def test_missing_signal_renormalization_matches_production():
    weights = {"text": .35, "image": .30, "location": .15, "time": .10, "category": .10}
    score, effective = combine_scores({"text": .8, "image": None, "location": .6, "time": .4, "category": 1.}, weights)
    assert sum(effective.values()) == pytest.approx(1.)
    assert "image" not in effective
    assert score == pytest.approx(sum({"text": .8, "location": .6, "time": .4, "category": 1.}[key] * value for key, value in effective.items()))


def test_experiment_model_stack_is_isolated():
    assert TEXT_CANDIDATE == "intfloat/e5-base-v2"
    assert IMAGE_CANDIDATE == "google/siglip-base-patch16-224"
    assert TUNING_SPLIT == "dev"
    assert TEXT_MODEL == "intfloat/e5-base-v2"
    assert IMAGE_MODEL == "google/siglip-base-patch16-224"
    assert WEIGHTS == {"text": .35, "image": .30, "location": .15, "time": .10, "category": .10}
