"""One-time generation of the frozen campus_v1 held-out test split."""
import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

from src.config import ROOT

SEED = 9107
ROOT_DIR = ROOT / "data" / "benchmark" / "campus_v1"
TEST_DIR = ROOT_DIR / "test"

# These physical-item families and wording are intentionally distinct from development cases.
CASES = [
    ("calculator", "Graphing calculator", "Electronics", "Graphing calculator in a translucent smoke cover; the seven key has a blue paint dot.", "Dark scientific calculator with a see-through grey shell and a tiny blue spot on key 7.", "Similar graphing calculator in a clear cover with an unmarked keypad.", "Engineering Building", "Engineering Building", "2026-10-04", "2026-10-05", "2026-10-05", "#3f464d", "blue-seven", ["similar_item", "ambiguous_description"], "both"),
    ("labcoat", "White laboratory coat", "Clothing", "Short white lab coat embroidered M.K. inside the collar and missing its lowest button.", "White practical coat with small M.K. stitching at the neck; bottom fastener absent.", "White lab coat of the same size with all buttons and no lettering.", "Science Building", "Science Building", "2026-10-05", "2026-10-06", "2026-10-06", "#e5e6e1", "collar-mk", ["similar_item"], "both"),
    ("lens", "Camera lens cap", "Other", "Black 58 mm lens cap with a faded silver crescent decal on the back.", "Round 58mm camera cover carrying a worn metallic moon sticker.", "Plain black 58 mm lens cap without a sticker.", "Lecture Hall", "Lecture Hall", "2026-10-06", "2026-10-07", "2026-10-07", "#242628", "moon-decal", ["similar_item", "ambiguous_description"], "both"),
    ("helmet", "Cycling helmet", "Other", "Teal bicycle helmet with a diagonal scrape above the left vent and a grey chin buckle.", "Blue-green riding helmet; slanted abrasion beside the left air opening, grey clasp.", "Teal cycling helmet with an intact shell and black buckle.", "Parking", "Gym", "2026-10-07", "2026-10-07", "2026-10-07", "#32828a", "left-abrasion", ["similar_item", "location_conflict"], "both"),
    ("drive", "Portable SSD", "Electronics", "Palm-sized silver external drive attached to a short cobalt USB cable.", "Compact metallic storage device with a brief bright-blue USB lead.", "Small silver external drive supplied with a short black cable.", "Computer Lab", "Computer Lab", "2026-10-08", "2026-10-09", "2026-10-09", "#aeb5b6", "cobalt-lead", ["similar_item"], "both"),
    ("mouse", "Wireless computer mouse", "Electronics", "Charcoal wireless mouse with the rear-left rubber foot missing.", "Dark cordless mouse; one glide pad is absent from the back-left underside.", "Charcoal wireless mouse with all four feet attached.", "Main Library", "Computer Lab", "2026-10-09", "2026-10-10", "2026-10-10", "#4a4b4e", "missing-foot", ["similar_item", "location_conflict"], "both"),
    ("ring", "Silver signet ring", "Other", "Small silver signet ring engraved with two parallel waves inside the band.", "Compact metallic seal ring with a pair of wavy lines etched on its inner surface.", "Small plain silver signet ring with a smooth inner band.", "Gym", "Gym", "2026-10-10", "2026-10-11", "2026-10-11", "#b8b9b5", "twin-waves", ["similar_item", "missing_lost_image"], "found_only"),
    ("lunchbox", "Olive lunch container", "Other", "Olive rectangular lunch box with one cream latch chipped at the corner.", "Green meal container; pale locking tab has a broken corner.", "Olive lunch container with two complete cream latches.", "Cafeteria", "Cafeteria", "2026-10-11", "2026-10-12", "2026-10-12", "#6d7650", "chipped-latch", ["similar_item"], "both"),
    ("flashdrive", "Orange USB drive", "Chargers / Accessories", "Orange USB flash drive on a tiny metal chain with a triangular bead.", "Bright tangerine memory stick attached to a short chain and three-sided charm.", "Orange flash drive on a plain key ring without a bead.", "Student Services", "Student Services", "2026-10-12", "2026-10-13", "2026-10-13", "#dd742f", "triangle-bead", ["similar_item", "category_conflict"], "both"),
    ("headphones", "Over-ear headphones", "Electronics", "Cream over-ear headphones with burgundy tape wrapped around the right hinge.", "Off-white full-size headset repaired with dark-red tape at its right joint.", "Cream over-ear headphones with an unrepaired right hinge.", "Student Center", "Student Center", "2026-10-13", "2026-10-14", "2026-10-14", "#ddd4bd", "burgundy-repair", ["similar_item", "missing_found_image"], "lost_only"),
    ("pencilcase", "Canvas pencil pouch", "Other", "Sand-coloured canvas pencil pouch with a violet ink blot near the brass zip.", "Beige fabric stationery case; purple stain beside its metal zipper.", "Beige canvas pencil pouch with a clean zipper edge.", "Reception", "Reception", "2026-10-14", "2026-10-15", "2026-10-15", "#b6a486", "violet-blot", ["similar_item"], "both"),
    ("goggles", "Laboratory safety goggles", "Other", "Clear safety goggles with a lime elastic strap and a cloudy patch over the right edge.", "Transparent lab eyewear, green band, small fogged area at the far-right lens.", "Clear safety goggles with a lime strap and fully transparent lenses.", "Science Building", "Science Building", "2026-10-15", "2026-10-16", "2026-10-16", "#c8ded7", "cloudy-edge", ["similar_item", "ambiguous_description"], "both"),
    ("tote", "Canvas tote bag", "Bags", "Natural canvas tote with a sewn orange hexagon patch below the left handle.", "Unbleached cloth carry bag bearing an orange six-sided badge near one strap.", "Plain natural canvas tote with no patch.", "Student Center", "Student Center", "2026-10-16", "2026-10-17", "2026-10-17", "#d7c7a4", "hex-patch", ["similar_item", "missing_both_images"], "none"),
    ("mug", "Insulated travel mug", "Water Bottles", "Copper travel mug with a navy sliding lid and shallow groove around its base.", "Bronze thermal cup, dark-blue slider top, narrow ring indentation near the bottom.", "Copper travel mug with a black lid and smooth base.", "Cafeteria", "Cafeteria", "2026-10-17", "2026-09-20", "2026-10-18", "#a56745", "base-groove", ["similar_item", "date_gap"], "both"),
    ("stylus", "Tablet stylus", "Chargers / Accessories", "White tablet pen with a mint rubber sleeve and a flattened replacement nib.", "Pale digital stylus in a light-green grip; substitute tip is visibly worn flat.", "White tablet stylus with a mint sleeve and pointed original nib.", "Engineering Building", "Engineering Building", "2026-10-18", "2026-10-19", "2026-10-19", "#e8e7df", "flat-nib", ["similar_item"], "both"),
    ("badge", "Conference name badge", "Student ID / Cards", "Guest conference badge in a blue-edged holder clipped to a yellow woven cord.", "Visitor event pass inside a navy-border sleeve on a golden fabric neck cord.", "Guest conference badge in a blue-edged holder on a black cord, found four weeks earlier.", "Lecture Hall", "Main Library", "2026-10-19", "2026-09-21", "2026-09-21", "#d9c64d", "yellow-cord", ["ambiguous_description", "date_gap", "location_conflict", "missing_both_images"], "none"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_fixture(family: str, color: str, mark: str, variant: int, path: Path) -> None:
    rng = random.Random(SEED * 1000 + variant)
    image = Image.new("RGB", (256, 256), rng.choice(["#d8e0e9", "#eadfd5", "#dce4d4"]))
    draw = ImageDraw.Draw(image)
    # Test fixtures use an offset diamond/oval composition, distinct from dev's rounded rectangle template.
    draw.polygon([(128, 34), (222, 128), (128, 222), (34, 128)], fill=color, outline="#3d4952", width=4)
    code = sum(ord(char) for char in family) % 4
    if code == 0:
        draw.ellipse((79, 94, 177, 162), outline="#f7f3e8", width=8)
    elif code == 1:
        draw.line((75, 94, 181, 162), fill="#f7f3e8", width=9)
        draw.line((181, 94, 75, 162), fill="#f7f3e8", width=9)
    elif code == 2:
        draw.rectangle((88, 89, 168, 167), outline="#f7f3e8", width=8)
    else:
        draw.arc((76, 75, 180, 179), 200, 520, fill="#f7f3e8", width=8)
    if mark and variant % 3 != 2:
        y = 68 + sum(ord(char) for char in mark) % 105
        draw.ellipse((184, y, 197, y + 13), fill="#6f244b")
    image.save(path)


def main() -> None:
    manifest_path = TEST_DIR / "manifest.json"
    if manifest_path.exists():
        raise SystemExit("Frozen test split already exists; refusing to regenerate or overwrite it.")
    images = TEST_DIR / "images"
    if TEST_DIR.exists() and any(TEST_DIR.iterdir()):
        raise SystemExit("Non-empty test directory exists without a frozen manifest; inspect it manually.")
    images.mkdir(parents=True, exist_ok=True)
    reports, qrels = [], {}
    for index, case in enumerate(CASES, 1):
        (family, name, category, lost_text, found_text, negative_text, location, negative_location,
         lost_date, found_date, negative_date, color, mark, tags, image_mode) = case
        lost_id, found_id, negative_id = 11000 + index, 12000 + index, 13000 + index
        paths = {"lost": None, "found": None, "negative": None}
        if image_mode in {"both", "lost_only"}:
            paths["lost"] = f"images/{lost_id}.png"; draw_fixture(family, color, mark, index * 3, TEST_DIR / paths["lost"])
        if image_mode in {"both", "found_only"}:
            paths["found"] = f"images/{found_id}.png"; draw_fixture(family, color, mark, index * 3 + 1, TEST_DIR / paths["found"])
        if image_mode != "none":
            paths["negative"] = f"images/{negative_id}.png"; draw_fixture(family, color, "", index * 3 + 2, TEST_DIR / paths["negative"])
        common = {"category": category, "location_detail": None, "handover_location": None}
        reports.extend([
            {"id": lost_id, "report_type": "lost", "name": name, "description": lost_text, "location": location,
             "identifying_details": mark, "event_date": lost_date, "image_path": paths["lost"], "challenge_tags": tags, **common},
            {"id": found_id, "report_type": "found", "name": f"Recovered {family}", "description": found_text, "location": location,
             "identifying_details": mark, "event_date": found_date, "image_path": paths["found"], "challenge_tags": tags, **common},
            {"id": negative_id, "report_type": "found", "name": f"Recovered {family}", "description": negative_text,
             "location": negative_location, "identifying_details": None, "event_date": negative_date,
             "image_path": paths["negative"], "challenge_tags": tags, **common},
        ])
        qrels[str(lost_id)] = {"relevant": [found_id], "hard_negatives": [negative_id], "challenge_tags": tags}
    reports_path, qrels_path = TEST_DIR / "reports.json", TEST_DIR / "qrels.json"
    reports_path.write_text(json.dumps({"split": "test", "reports": reports}, indent=2), encoding="utf-8")
    qrels_path.write_text(json.dumps({"split": "test", "qrels": qrels}, indent=2), encoding="utf-8")
    image_hashes = {path.name: sha256(path) for path in sorted(images.glob("*.png"))}
    manifest = {"benchmark": "campus_v1", "split": "test", "status": "frozen", "seed": SEED,
                "pairs": len(CASES), "reports": len(reports), "candidate_count": len([x for x in reports if x["report_type"] == "found"]),
                "generator": "scripts/generate_final_test.py", "reports_sha256": sha256(reports_path),
                "qrels_sha256": sha256(qrels_path), "image_sha256": image_hashes,
                "immutability": "Do not regenerate, edit, or relabel after final evaluation begins."}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    root_manifest = json.loads((ROOT_DIR / "manifest.json").read_text())
    root_manifest.update(test_pairs=len(CASES), test_seed=SEED, test_status="frozen")
    (ROOT_DIR / "manifest.json").write_text(json.dumps(root_manifest, indent=2), encoding="utf-8")
    print(f"Generated and froze campus_v1 test: {len(CASES)} pairs, {len(reports)} reports, {len(image_hashes)} images")


if __name__ == "__main__":
    main()
