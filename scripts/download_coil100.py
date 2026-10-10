"""Download and safely extract COIL-100 from Columbia CAVE."""
import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path

from src.config import ROOT

URL = "https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-100/coil-100.zip"
DEST = ROOT / "data" / "external" / "coil100"
ARCHIVE = DEST / "coil-100.zip"
IMAGES = DEST / "images"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    if len(list(IMAGES.glob("obj*__*.png"))) == 7200:
        print(f"COIL-100 already ready at {IMAGES}")
        return
    if not ARCHIVE.exists():
        temporary = ARCHIVE.with_suffix(".download")
        print(f"Downloading {URL}")
        with urllib.request.urlopen(URL, timeout=120) as response, temporary.open("wb") as target:
            shutil.copyfileobj(response, target)
        temporary.replace(ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as source:
        members = [item for item in source.infolist() if not item.is_dir() and item.filename.lower().endswith(".png")]
        if len(members) != 7200:
            raise ValueError(f"Expected 7200 PNG files, found {len(members)}")
        IMAGES.mkdir(parents=True, exist_ok=True)
        for member in members:
            name = Path(member.filename).name
            if not name.startswith("obj") or "__" not in name:
                raise ValueError(f"Unexpected archive member: {member.filename}")
            with source.open(member) as incoming, (IMAGES / name).open("wb") as outgoing:
                shutil.copyfileobj(incoming, outgoing)
    print(f"Extracted 7200 images; archive SHA-256 {hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
