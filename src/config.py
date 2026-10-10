"""Central configuration. Paths are resolved relative to the repository."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_DIR = Path(os.getenv("FINDIT_DATA_DIR", str(ROOT / "data")))
if not DATA_DIR.is_absolute():
    DATA_DIR = ROOT / DATA_DIR
UPLOAD_DIR = DATA_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"
DATABASE_URL = f"sqlite:///{(DATA_DIR / 'findit.db').as_posix()}"
TEXT_MODEL = os.getenv("FINDIT_TEXT_MODEL", "intfloat/e5-base-v2")
IMAGE_MODEL = os.getenv("FINDIT_IMAGE_MODEL", "google/siglip-base-patch16-224")
DEVICE = os.getenv("FINDIT_DEVICE", "cpu")
WEIGHTS = {"text": 0.35, "image": 0.30, "location": 0.15, "time": 0.10, "category": 0.10}
TIME_DECAY_DAYS = 14.0
EARLY_FOUND_PENALTY = 0.5
HIGH_MATCH = 0.80
POSSIBLE_MATCH = 0.55
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
CATEGORIES = ["Electronics", "Student ID / Cards", "Keys", "Bags", "Wallets", "Clothing",
              "Books / Notes", "Chargers / Accessories", "Glasses", "Water Bottles", "Other"]
CAMPUS_LOCATIONS = ["Main Library", "Student Center", "Engineering Building", "Science Building",
                    "Cafeteria", "Computer Lab", "Lecture Hall", "Gym", "Parking", "Reception",
                    "Security Office", "Student Services"]
HANDOVER_LOCATIONS = ["Campus Security", "Main Reception", "Library Desk", "Student Services",
                      "Finder still has item", "Other approved campus location"]
STAFF_KEY = os.getenv("FINDIT_STAFF_KEY", "demo-staff-key")
