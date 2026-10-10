"""Lazy pretrained models and content-addressed embedding caches."""
import hashlib
import logging
from functools import lru_cache
from pathlib import Path
from threading import RLock
from uuid import uuid4

import numpy as np
from PIL import Image

from src.config import CACHE_DIR, DEVICE, IMAGE_MODEL, TEXT_MODEL

logger = logging.getLogger(__name__)
_lock = RLock()


class ModelUnavailable(RuntimeError):
    """Model download/inference failed; callers must not silently substitute scores."""


@lru_cache(maxsize=2)
def load_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading %s on %s", model_name, DEVICE)
        return SentenceTransformer(model_name, device=DEVICE, trust_remote_code=False)
    except Exception as exc:
        logger.exception("Could not load model %s", model_name)
        raise ModelUnavailable(f"Could not load {model_name}. Check the server log and model download connection; use baseline mode meanwhile.") from exc


@lru_cache(maxsize=1)
def load_image_model(model_name: str):
    try:
        from transformers import AutoImageProcessor, AutoModel
        logger.info("Loading image encoder %s on %s", model_name, DEVICE)
        processor = AutoImageProcessor.from_pretrained(model_name, trust_remote_code=False)
        model = AutoModel.from_pretrained(model_name, trust_remote_code=False).to(DEVICE).eval()
        return model, processor
    except Exception as exc:
        logger.exception("Could not load image encoder %s", model_name)
        raise ModelUnavailable(f"Could not load {model_name}. Check the server log and model download connection; use baseline mode meanwhile.") from exc


def _cached_embedding(kind: str, payload: bytes, image_path: Path | None = None) -> np.ndarray:
    model_name = TEXT_MODEL if kind == "text" else IMAGE_MODEL
    # Include preprocessing version and model identifier; changing either invalidates cache.
    key = hashlib.sha256(f"v1:{kind}:{model_name}:".encode() + payload).hexdigest()
    cache_path = CACHE_DIR / f"{key}.npy"
    with _lock:
        if cache_path.exists():
            try:
                return np.load(cache_path, allow_pickle=False)
            except (OSError, ValueError):
                logger.warning("Rebuilding unreadable embedding cache %s", key)
        try:
            if image_path is None:
                model = load_model(model_name)
                vector = model.encode(payload.decode("utf-8"), normalize_embeddings=True, show_progress_bar=False)
            else:
                import torch
                model, processor = load_image_model(model_name)
                with Image.open(image_path) as source:
                    inputs = {key: value.to(DEVICE) for key, value in processor(images=[source.convert("RGB")], return_tensors="pt").items()}
                with torch.inference_mode():
                    vector = model.get_image_features(**inputs)
                    vector = torch.nn.functional.normalize(vector, dim=-1)[0].cpu().numpy()
            vector = np.asarray(vector, dtype=np.float32)
            if vector.ndim != 1 or not np.isfinite(vector).all():
                raise ValueError("Model returned an invalid embedding")
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            temporary = cache_path.with_name(f"{key}.{uuid4().hex}.tmp")
            try:
                with temporary.open("wb") as file:
                    np.save(file, vector, allow_pickle=False)
                temporary.replace(cache_path)
            finally:
                temporary.unlink(missing_ok=True)
            return vector
        except ModelUnavailable:
            raise
        except Exception as exc:
            logger.exception("Embedding inference failed")
            raise ModelUnavailable("Embedding inference failed. Check the server log; baseline mode remains available.") from exc


def text_embedding(text: str) -> np.ndarray:
    return _cached_embedding("text", text.encode("utf-8"))


def image_embedding(path: Path) -> np.ndarray:
    try:
        return _cached_embedding("image", path.read_bytes(), path)
    except OSError as exc:
        raise ModelUnavailable("A stored report image cannot be read. Re-upload the image or use text/baseline mode.") from exc
