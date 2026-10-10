"""Validate decoded images and store re-encoded pixels under generated names."""
import io
import warnings
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from src.config import MAX_IMAGE_BYTES, MAX_IMAGE_PIXELS, UPLOAD_DIR


def image_file(name: str) -> Path:
    if Path(name).name != name or not name.endswith(".jpg") or len(name) != 36:
        raise ValueError("Invalid image identifier")
    try:
        int(name[:-4], 16)
    except ValueError as exc:
        raise ValueError("Invalid image identifier") from exc
    return UPLOAD_DIR / name


def save_image(content: bytes) -> str:
    if not content or len(content) > MAX_IMAGE_BYTES:
        raise ValueError("Image must be nonempty and no larger than 8 MB")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as probe:
                if probe.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValueError("Only JPEG, PNG and WebP images are supported")
                if probe.width * probe.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image exceeds the 20 megapixel limit")
                probe.verify()
            with Image.open(io.BytesIO(content)) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((1600, 1600))
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                name = f"{uuid4().hex}.jpg"
                # Re-encoding discards filename, metadata and any appended payload.
                image.save(image_file(name), format="JPEG", quality=90)
                return name
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("Invalid or unsafe image file") from exc
