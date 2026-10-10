"""Generate campus_v1 development benchmark with lightweight procedural images.

The reports are synthetic. Images are deliberately simple, deterministic fixtures;
benchmark difficulty comes primarily from hard negatives and conflicting metadata.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

from src.config import ROOT

ROOT_DIR = ROOT / "data" / "benchmark" / "campus_v1"
DEV_DIR = ROOT_DIR / "dev"

# family, lost name, category, lost description, found paraphrase, hard-negative description,
# location, negative location, lost date, found date, negative date, color, mark, tags, image mode
CASES = [
    ("earbuds", "Black AirPods Pro", "Electronics", "Black AirPods Pro case with a tiny white scratch near the front-right corner.", "Dark Apple wireless earbuds in a black charging case; a small pale nick sits by the right edge.", "Black AirPods Pro case in clean condition with no visible marks.", "Main Library", "Main Library", "2026-09-03", "2026-09-04", "2026-09-04", "#202322", "scratch", ["similar_item", "ambiguous_description"], "both"),
    ("earbuds", "White wireless earbuds", "Electronics", "White earbuds in a cream silicone case with a blue carabiner.", "Pale wireless earphones with an off-white cover and blue clip attached.", "White earbuds in a plain hard case without a clip.", "Student Center", "Main Library", "2026-09-06", "2026-09-06", "2026-09-06", "#eee9dc", "clip", ["similar_item", "location_conflict"], "both"),
    ("backpack", "Navy backpack", "Bags", "Navy backpack with mustard front pocket and a silver zipper pull.", "Dark blue school bag with a yellow outer pouch and metallic zip tab.", "Navy backpack with a yellow pocket but a red fabric zipper pull.", "Student Center", "Student Center", "2026-09-08", "2026-09-09", "2026-09-09", "#253b68", "yellow-pocket", ["similar_item"], "both"),
    ("backpack", "Black laptop bag", "Bags", "Plain black laptop backpack with red fox keychain on the left strap.", "Dark computer rucksack carrying a small crimson animal charm.", "Black laptop backpack with no keychain and a reflective strip.", "Engineering Building", "Engineering Building", "2026-09-10", "2026-09-11", "2026-09-11", "#25272a", "red-charm", ["similar_item", "ambiguous_description"], "both"),
    ("charger", "USB-C laptop charger", "Chargers / Accessories", "White 65 watt USB-C charging brick with grey tape around the cable.", "Pale 65W type-C power adapter; lead has a grey taped section.", "White USB-C charger with the same size brick but an unmarked cable.", "Computer Lab", "Computer Lab", "2026-09-12", "2026-09-13", "2026-09-13", "#ecebe4", "tape", ["similar_item"], "both"),
    ("cable", "Braided phone cable", "Chargers / Accessories", "Two metre black braided Lightning cable with a bent connector.", "Long woven dark phone lead; Lightning tip is slightly crooked.", "Two metre black braided USB-C cable in good condition.", "Lecture Hall", "Lecture Hall", "2026-09-12", "2026-09-14", "2026-09-14", "#303335", "bent-tip", ["similar_item", "category_conflict"], "both"),
    ("keys", "Three campus keys", "Keys", "Three silver keys on one ring with a round blue plastic fob.", "Keyring containing three metal keys and a circular blue tag.", "Three silver keys with a square blue fob.", "Parking", "Parking", "2026-09-15", "2026-09-15", "2026-09-15", "#3b7fc4", "round-fob", ["similar_item"], "both"),
    ("keys", "Keys on red lanyard", "Keys", "Two keys and a small brass key on a faded red university lanyard.", "Pair of silver keys plus a brass one attached to a worn crimson neck strap.", "Two keys on a new bright red lanyard without a brass key.", "Science Building", "Science Building", "2026-09-16", "2026-09-17", "2026-09-17", "#b23c3c", "brass-key", ["similar_item"], "both"),
    ("wallet", "Black leather wallet", "Wallets", "Black folding wallet with red stitching and a small crease inside.", "Dark leather billfold edged in crimson thread with an inner fold mark.", "Black wallet with red stitching and no crease, found weeks earlier.", "Cafeteria", "Cafeteria", "2026-09-18", "2026-09-19", "2026-08-25", "#262527", "red-stitch", ["similar_item", "date_gap"], "both"),
    ("wallet", "Brown card holder", "Wallets", "Slim brown card holder with four slots and initials stamped inside.", "Tan narrow card case with four pockets and small pressed initials.", "Brown four-slot card holder with no stamped letters.", "Student Services", "Student Services", "2026-09-19", "2026-09-20", "2026-09-20", "#79533e", "initials", ["similar_item"], "both"),
    ("card", "Student ID card", "Student ID / Cards", "Campus ID in a clear holder on a dark green lanyard.", "University card inside a transparent sleeve attached to a forest-green strap.", "Campus card in a clear holder on a black lanyard.", "Main Library", "Student Center", "2026-09-20", "2026-09-20", "2026-09-20", "#47745a", "green-strap", ["similar_item", "location_conflict", "ambiguous_description"], "both"),
    ("card", "Blue access card", "Student ID / Cards", "Plain blue access card inside a frosted sleeve with one cracked corner.", "Blue campus entry card in a cloudy holder; sleeve corner is split.", "Blue access card in an undamaged frosted holder.", "Engineering Building", "Engineering Building", "2026-09-21", "2026-09-22", "2026-09-22", "#4775ad", "cracked-sleeve", ["similar_item"], "both"),
    ("glasses", "Round reading glasses", "Glasses", "Round tortoiseshell glasses with a loose left hinge.", "Circular brown mottled spectacles; left arm hinge wiggles.", "Round tortoiseshell glasses with firm hinges.", "Reception", "Reception", "2026-09-23", "2026-09-23", "2026-09-23", "#80563e", "loose-hinge", ["similar_item"], "both"),
    ("glasses", "Black rectangular glasses", "Glasses", "Black rectangular glasses in a purple zip case.", "Dark square-frame spectacles stored in a violet zipped holder.", "Black rectangular glasses in a plain black case.", "Lecture Hall", "Lecture Hall", "2026-09-23", "2026-09-24", "2026-09-24", "#28292c", "purple-case", ["similar_item"], "both"),
    ("bottle", "Blue metal bottle", "Water Bottles", "Blue steel bottle with a dent near the base and one astronomy sticker.", "Metallic navy flask, lower edge dented, with a single planet decal.", "Blue steel bottle with several stickers and no dent.", "Gym", "Gym", "2026-09-24", "2026-09-25", "2026-09-25", "#2f6092", "dent-sticker", ["similar_item"], "both"),
    ("bottle", "Black water bottle", "Water Bottles", "Matte black one-litre bottle with orange cap and scratched handle.", "Large dark flask with a bright orange lid and scuffed carry loop.", "Matte black bottle with orange cap and an intact handle.", "Cafeteria", "Gym", "2026-09-25", "2026-09-25", "2026-09-25", "#27292a", "orange-cap", ["similar_item", "location_conflict"], "both"),
    ("book", "Calculus textbook", "Books / Notes", "Blue calculus textbook, third edition, with handwritten notes on chapter four.", "Third-edition blue calculus book containing pencil annotations in chapter 4.", "Same blue calculus title, second edition, with no notes.", "Main Library", "Main Library", "2026-09-26", "2026-09-27", "2026-09-27", "#315e91", "chapter-notes", ["similar_item"], "both"),
    ("notebook", "Green spiral notebook", "Books / Notes", "A5 green spiral notebook with a torn back cover and statistics notes.", "Small green wire-bound pad, back cover ripped, filled with statistics writing.", "A5 green spiral notebook with an intact cover and chemistry notes.", "Science Building", "Science Building", "2026-09-27", "2026-09-28", "2026-09-28", "#4f7956", "torn-cover", ["similar_item", "ambiguous_description"], "both"),
    ("hoodie", "Grey campus hoodie", "Clothing", "Grey university hoodie with blue ink mark on the right cuff.", "Heather-grey campus sweatshirt; small navy stain on right sleeve cuff.", "Grey university hoodie with clean cuffs.", "Student Center", "Student Center", "2026-09-28", "2026-09-29", "2026-09-29", "#87898a", "ink-cuff", ["similar_item", "missing_lost_image"], "found_only"),
    ("scarf", "Red striped scarf", "Clothing", "Red wool scarf with narrow white stripes and one frayed end.", "Crimson knitted neck scarf with thin pale bands and a worn edge.", "Red and white striped scarf with both ends intact.", "Student Services", "Student Services", "2026-09-29", "2026-09-30", "2026-09-30", "#b34242", "frayed-end", ["similar_item", "missing_found_image"], "lost_only"),
    ("phone", "Phone in green case", "Electronics", "Phone in a dark green case with a small white star sticker.", "Smartphone protected by a forest-coloured cover carrying one pale star decal.", "Phone in a dark green case without any sticker.", "Lecture Hall", "Lecture Hall", "2026-09-30", "2026-10-01", "2026-10-01", "#36714c", "star", ["similar_item", "missing_both_images"], "none"),
    ("watch", "Silver wristwatch", "Other", "Round silver watch with black leather strap and a faint crack at six o'clock.", "Analog silver timepiece on a dark leather band; hairline split below the dial.", "Round silver watch with black strap and an uncracked face.", "Science Building", "Reception", "2026-10-01", "2026-10-02", "2026-10-02", "#b5b8b8", "dial-crack", ["similar_item", "location_conflict"], "both"),
    ("umbrella", "Navy umbrella", "Other", "Compact navy umbrella with a curved wooden handle and loose wrist strap.", "Small dark-blue rain umbrella, bent wood grip, slack carrying loop.", "Compact navy umbrella with a straight plastic handle.", "Reception", "Reception", "2026-10-01", "2026-10-02", "2026-10-02", "#34496b", "wood-handle", ["ambiguous_description", "missing_both_images"], "none"),
    ("earbuds", "Black earbuds", "Electronics", "Black wireless earbuds in a black case; unsure of brand, tiny chip on lid.", "Dark unbranded earphones in a matching case with a minute nick on top.", "Black wireless earbuds in an identical-looking case found three weeks earlier.", "Main Library", "Main Library", "2026-10-02", "2026-10-03", "2026-09-11", "#222424", "lid-chip", ["ambiguous_description", "date_gap", "similar_item"], "both"),
]


def draw_fixture(family: str, color: str, mark: str, variant: int, path: Path) -> None:
    rng = random.Random(4101 + variant)
    image = Image.new("RGB", (256, 256), rng.choice(["#e7e3da", "#e2e7e4", "#e8e4d9"]))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((48, 55, 208, 202), radius=28, fill=color, outline="#566158", width=3)
    # A stable family glyph and a small mark make relevant/negative fixtures similar but not identical.
    family_code = sum(ord(char) for char in family) % 5
    if family_code == 0:
        draw.ellipse((88, 88, 168, 168), outline="#f2f2eb", width=7)
    elif family_code == 1:
        draw.rectangle((86, 88, 170, 170), outline="#f2f2eb", width=7)
    elif family_code == 2:
        draw.line((80, 128, 176, 128), fill="#f2f2eb", width=9)
    elif family_code == 3:
        draw.arc((77, 77, 179, 179), 20, 330, fill="#f2f2eb", width=7)
    else:
        draw.polygon([(128, 75), (176, 172), (80, 172)], outline="#f2f2eb")
    if mark and variant % 3 != 2:
        x = 75 + (sum(ord(c) for c in mark) % 95)
        draw.line((x, 178, x + 18, 174), fill="#f8d66d", width=5)
    image.save(path)


def generate_dev() -> dict:
    if (ROOT_DIR / "test" / "manifest.json").exists():
        raise RuntimeError("Frozen test split exists; refusing to regenerate development data")
    image_dir = DEV_DIR / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    reports, qrels = [], {}
    for index, case in enumerate(CASES, 1):
        (family, name, category, lost_text, found_text, negative_text, location, negative_location,
         lost_date, found_date, negative_date, color, mark, tags, image_mode) = case
        lost_id, found_id, negative_id = 1000 + index, 2000 + index, 3000 + index
        paths = {"lost": None, "found": None, "negative": None}
        if image_mode in {"both", "lost_only"}:
            paths["lost"] = f"images/{lost_id}.png"
            draw_fixture(family, color, mark, index * 3, DEV_DIR / paths["lost"])
        if image_mode in {"both", "found_only"}:
            paths["found"] = f"images/{found_id}.png"
            draw_fixture(family, color, mark, index * 3 + 1, DEV_DIR / paths["found"])
        if image_mode != "none":
            paths["negative"] = f"images/{negative_id}.png"
            draw_fixture(family, color, "", index * 3 + 2, DEV_DIR / paths["negative"])
        common = {"category": category, "location_detail": None, "handover_location": None}
        reports.extend([
            {"id": lost_id, "report_type": "lost", "name": name, "description": lost_text,
             "location": location, "identifying_details": mark, "event_date": lost_date,
             "image_path": paths["lost"], "challenge_tags": tags, **common},
            {"id": found_id, "report_type": "found", "name": f"Found {family}", "description": found_text,
             "location": location, "identifying_details": mark, "event_date": found_date,
             "image_path": paths["found"], "challenge_tags": tags, **common},
            {"id": negative_id, "report_type": "found", "name": f"Found {family}", "description": negative_text,
             "location": negative_location, "identifying_details": None, "event_date": negative_date,
             "image_path": paths["negative"], "challenge_tags": tags, **common},
        ])
        qrels[str(lost_id)] = {"relevant": [found_id], "hard_negatives": [negative_id], "challenge_tags": tags}
    reports_path, qrels_path = DEV_DIR / "reports.json", DEV_DIR / "qrels.json"
    reports_path.write_text(json.dumps({"split": "dev", "reports": reports}, indent=2), encoding="utf-8")
    qrels_path.write_text(json.dumps({"split": "dev", "qrels": qrels}, indent=2), encoding="utf-8")
    manifest = {"benchmark": "findit-campus-v1", "provenance": "Entirely synthetic campus reports and lightweight procedural fixtures.",
                "development_pairs": len(CASES), "test_pairs": 0, "dev_seed": 4101,
                "test_status": "not_generated", "production_ranker_changed": False}
    (ROOT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ROOT_DIR / "README.md").write_text(
        "# FindIt campus_v1 benchmark\n\nDevelopment split only: 24 synthetic known pairs plus one hard negative per query. "
        "The final test split is intentionally not generated. Images are deterministic fixtures, not real photos.\n",
        encoding="utf-8")
    return {"reports": len(reports), "pairs": len(qrels)}


if __name__ == "__main__":
    summary = generate_dev()
    print(f"Generated campus_v1 dev: {summary['pairs']} pairs, {summary['reports']} reports")
