"""Pure scoring functions; unavailable signals are None, never zero."""
import math
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher

import numpy as np

from src.config import EARLY_FOUND_PENALTY, HIGH_MATCH, POSSIBLE_MATCH, TIME_DECAY_DAYS, WEIGHTS


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))


def keyword_similarity(left: str, right: str) -> float:
    """Token Jaccard baseline: intersection divided by union."""
    a, b = set(normalize_text(left).split()), set(normalize_text(right).split())
    return len(a & b) / len(a | b) if a | b else 0.0


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    """Clip negative cosine to zero so each ranking component is in [0, 1]."""
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    return float(np.clip(np.dot(left, right) / denominator, 0, 1)) if denominator else 0.0


def location_similarity(left: str | None, right: str | None) -> float | None:
    a, b = normalize_text(left or ""), normalize_text(right or "")
    if not a or not b:
        return None
    if a == b:
        return 1.0
    return 0.8 * max(keyword_similarity(a, b), SequenceMatcher(None, a, b).ratio())


def time_similarity(lost: date | None, found: date | None, decay_days: float = TIME_DECAY_DAYS) -> float | None:
    if decay_days <= 0:
        raise ValueError("decay_days must be positive")
    if lost is None or found is None:
        return None
    gap = (found - lost).days
    return math.exp(-abs(gap) / decay_days) * (EARLY_FOUND_PENALTY if gap < 0 else 1.0)


def category_similarity(left: str | None, right: str | None) -> float | None:
    if not left or not right:
        return None
    a, b = normalize_text(left), normalize_text(right)
    if a == "other" or b == "other":
        return 0.5
    return 1.0 if a == b else 0.15


def combine_scores(components: dict[str, float | None], weights: dict[str, float] | None = None) -> tuple[float, dict[str, float]]:
    """Renormalize positive weights across the signals actually available."""
    weights = WEIGHTS if weights is None else weights
    if any(not math.isfinite(w) or w < 0 for w in weights.values()):
        raise ValueError("Weights must be finite and nonnegative")
    available = {}
    for key, score in components.items():
        if score is not None:
            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError("Scores must be finite and in [0, 1]")
            if weights.get(key, 0) > 0:
                available[key] = weights[key]
    total = sum(available.values())
    if total == 0:
        raise ValueError("No positively weighted signals are available")
    effective = {key: weight / total for key, weight in available.items()}
    return sum(float(components[key]) * weight for key, weight in effective.items()), effective


def match_label(score: float) -> str:
    return "High Match" if score >= HIGH_MATCH else "Possible Match" if score >= POSSIBLE_MATCH else "Low Match"
