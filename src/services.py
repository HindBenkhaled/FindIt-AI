"""One ranking service shared by the API and offline evaluation."""
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from src import embeddings
from src.config import WEIGHTS
from src.matching import (category_similarity, combine_scores, cosine_similarity,
                          keyword_similarity, location_similarity, match_label, time_similarity)
from src.storage import image_file

METHOD_WEIGHTS = {
    "keyword": {"text": 1.0},
    "baseline": {k: v for k, v in WEIGHTS.items() if k != "image"},
    "text": {"text": 1.0},
    "image": {"image": 1.0},
    "text_image": {"text": WEIGHTS["text"], "image": WEIGHTS["image"]},
    "full": WEIGHTS,
}


def report_text(item: Any) -> str:
    # Private fields improve internal matching but are never serialized by public routes.
    details = getattr(item, "identifying_details", None) or ""
    location_detail = getattr(item, "location_detail", None) or ""
    return f"{item.name}. {item.description}. {details}. {location_detail}"


def rank_reports(query: Any, candidates: Sequence[Any], method: str = "full",
                 resolve_image: Callable[[str], Path] = image_file) -> list[dict]:
    """Rank found reports with explicit signal availability and deterministic ties.

    Image-only mode excludes candidates lacking images and rejects an imageless
    query. Other methods redistribute missing image weights for each pair.
    """
    if query.report_type != "lost":
        raise ValueError("Select a lost report to find matching found reports")
    if method not in METHOD_WEIGHTS:
        raise ValueError("Unknown matching method")
    if method == "image" and not query.image_path:
        raise ValueError("Image-only matching requires an image on the lost report")
    candidates = [item for item in candidates if item.report_type == "found"]
    if not candidates:
        return []
    weights = METHOD_WEIGHTS[method]
    use_text_ai = method in {"text", "text_image", "full"}
    use_images = method in {"image", "text_image", "full"}
    query_text = embeddings.text_embedding(report_text(query)) if use_text_ai else None
    query_image = None
    if use_images and query.image_path and any(item.image_path for item in candidates):
        query_image = embeddings.image_embedding(resolve_image(query.image_path))
    results = []
    for item in candidates:
        if method == "image" and not item.image_path:
            continue
        signals = dict.fromkeys(WEIGHTS)
        if "text" in weights:
            signals["text"] = (
                cosine_similarity(query_text, embeddings.text_embedding(report_text(item)))
                if use_text_ai else keyword_similarity(report_text(query), report_text(item))
            )
        if query_image is not None and item.image_path:
            signals["image"] = cosine_similarity(query_image, embeddings.image_embedding(resolve_image(item.image_path)))
        if "location" in weights:
            signals["location"] = location_similarity(query.location, item.location)
            signals["time"] = time_similarity(query.event_date, item.event_date)
            signals["category"] = category_similarity(query.category, item.category)
        score, effective = combine_scores(signals, weights)
        results.append({"item": item, "score": score, "label": match_label(score),
                        "components": signals, "effective_weights": effective})
    return sorted(results, key=lambda result: (-result["score"], result["item"].id))
