"""Build the deterministic COIL-100 exact-object retrieval protocol."""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from src.config import ROOT

SOURCE = ROOT / "data" / "external" / "coil100" / "images"
DEST = ROOT / "data" / "benchmark" / "image_retrieval" / "coil100_v1"
PATTERN = re.compile(r"obj(?P<object>\d+)__(?P<angle>\d+)\.png$")
QUERY_ANGLES = (0, 180)
GALLERIES = {"easy": (5, 185), "hard": (90, 270)}


def image_id(obj: int, angle: int) -> str:
    return f"obj{obj:03d}_view{angle:03d}"


def main() -> None:
    available = {}
    for path in SOURCE.glob("obj*__*.png"):
        match = PATTERN.match(path.name)
        if match:
            available[(int(match["object"]), int(match["angle"]))] = path
    expected = {(obj, angle) for obj in range(1, 101) for angle in range(0, 360, 5)}
    missing = expected - available.keys()
    if missing:
        raise SystemExit(f"COIL-100 is incomplete; missing {len(missing)} files. Run scripts.download_coil100.")
    queries = [{"id": image_id(obj, angle), "object_id": obj, "angle": angle,
                "path": str(available[(obj, angle)].relative_to(ROOT)).replace("\\", "/")}
               for obj in range(1, 101) for angle in QUERY_ANGLES]
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "queries.json").write_text(json.dumps(queries, indent=2), encoding="utf-8")
    protocol_hashes = {}
    for difficulty, angles in GALLERIES.items():
        gallery = [{"id": image_id(obj, angle), "object_id": obj, "angle": angle,
                    "path": str(available[(obj, angle)].relative_to(ROOT)).replace("\\", "/")}
                   for obj in range(1, 101) for angle in angles]
        qrels = {query["id"]: {"relevant": [entry["id"] for entry in gallery
                                               if entry["object_id"] == query["object_id"]]}
                 for query in queries}
        (DEST / f"gallery_{difficulty}.json").write_text(json.dumps(gallery, indent=2), encoding="utf-8")
        (DEST / f"qrels_{difficulty}.json").write_text(json.dumps(qrels, indent=2), encoding="utf-8")
        protocol_hashes[difficulty] = hashlib.sha256(
            (DEST / f"gallery_{difficulty}.json").read_bytes() + (DEST / f"qrels_{difficulty}.json").read_bytes()
        ).hexdigest()
    manifest = {
        "name": "coil100_v1", "dataset": "Columbia Object Image Library (COIL-100)",
        "objects": 100, "query_count": 200, "gallery_size_per_setting": 200, "seed": None,
        "query_angles": list(QUERY_ANGLES), "gallery_angles": {k: list(v) for k, v in GALLERIES.items()},
        "selection": "Fixed angles; two queries and two gallery views per physical object.",
        "self_exclusion": "Query angles never occur in either gallery.",
        "relevance": "Exact physical object identity only; two relevant gallery images per query.",
        "protocol_hashes": protocol_hashes,
    }
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    provenance = {
        "dataset": "COIL-100", "source_organization": "Columbia University CAVE",
        "source_url": "https://www.cs.columbia.edu/CAVE/software/softlib/coil-100.php",
        "download_url": "https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-100/coil-100.zip",
        "citation": "S. A. Nene, S. K. Nayar and H. Murase, CUCS-006-96 (1996)",
        "terms": "The official page provides public download access but does not state a standardized license. Treat as research/academic data; do not redistribute images.",
        "accessed": date.today().isoformat(),
    }
    archive = ROOT / "data" / "external" / "coil100" / "coil-100.zip"
    if archive.is_file():
        provenance["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    (DEST / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(f"Built coil100_v1: {len(queries)} queries, 200 candidates per setting")


if __name__ == "__main__":
    main()
