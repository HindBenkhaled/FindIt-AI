"""Reproducible, explicitly synthetic reports and procedural image fixtures.

These illustrations are test fixtures, not photographs or collected evidence.
No text labels or report identifiers are rendered into the pixels.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

from src.config import ROOT

DEST = ROOT / "data" / "synthetic"
# name, category, lost description, found description, location, kind, color
EXAMPLES = [
    ("AirPods Pro", "Electronics", "Black Apple earbuds case, white scratch on front.", "Wireless earphones in a dark charging box with a pale mark.", "Main Library", "earbuds", "#272727"),
    ("Leather wallet", "Wallets", "Black leather wallet with red stitching, two card slots.", "Dark folding billfold with crimson thread around the edge.", "Cafeteria", "wallet", "#252528"),
    ("Campus keys", "Keys", "Three silver keys on a ring with a blue round tag.", "Keyring holding three door keys and a blue circular fob.", "Parking", "keys", "#2475d5"),
    ("Blue backpack", "Bags", "Navy backpack with yellow front pocket and two straps.", "Dark blue school rucksack with a mustard pouch on the front.", "Student Center", "backpack", "#233b6b"),
    ("Wristwatch", "Other", "Round silver watch with black leather strap and white dial.", "Analog timepiece, pale round face, dark band.", "Science Building", "watch", "#303030"),
    ("Mobile phone", "Electronics", "Green phone case with two cameras and a small white star.", "Smartphone in a forest green cover with a star sticker.", "Lecture Hall", "phone", "#287749"),
    ("Laptop charger", "Chargers / Accessories", "White rectangular USB C power adapter and coiled cable.", "Pale laptop charging brick with a type C lead.", "Computer Lab", "charger", "#eeeeee"),
    ("Reading glasses", "Glasses", "Brown round spectacles with thin frames.", "Circular tortoiseshell eyeglasses with slender arms.", "Reception", "glasses", "#805539"),
]


def draw_fixture(kind: str, color: str, variant: int, path: Path) -> None:
    """Draw simple item shapes with deterministic changes in view/background."""
    rng = random.Random(100 + variant)
    image = Image.new("RGB", (320, 320), rng.choice(["#ded9d0", "#e1e5e8", "#e5decc"]))
    layer = Image.new("RGBA", image.size)
    d = ImageDraw.Draw(layer)
    if kind == "earbuds":
        d.rounded_rectangle((65, 110, 255, 225), radius=38, fill=color, outline="#555555", width=3)
        d.line((70, 146, 250, 146), fill="#aaaaaa", width=2)
        d.line((148, 182, 174, 178), fill="white", width=3)
    elif kind == "wallet":
        d.rounded_rectangle((58, 92, 265, 235), radius=12, fill=color)
        d.rounded_rectangle((65, 99, 258, 228), radius=9, outline="#b83b3b", width=3)
        d.line((163, 96, 163, 230), fill="#444444", width=3)
        d.line((78, 138, 145, 138), fill="#999999", width=2)
        d.line((78, 163, 145, 163), fill="#999999", width=2)
    elif kind == "keys":
        d.ellipse((105, 64, 189, 148), outline="#999999", width=8)
        for x, y in [(118, 122), (154, 134), (186, 119)]:
            d.ellipse((x-12, y-12, x+12, y+12), fill="#bbbbbb", outline="#777777", width=3)
            d.line((x, y+10, x, y+102), fill="#aaaaaa", width=10)
            d.line((x, y+80, x+16, y+80), fill="#aaaaaa", width=8)
        d.ellipse((65, 133, 116, 184), fill=color)
    elif kind == "backpack":
        d.rounded_rectangle((117, 40, 203, 98), radius=20, outline=color, width=12)
        d.rounded_rectangle((78, 68, 245, 274), radius=38, fill=color)
        d.rounded_rectangle((99, 168, 224, 248), radius=16, fill="#d3b63b")
        d.line((110, 181, 212, 181), fill="#555555", width=4)
    elif kind == "watch":
        d.rounded_rectangle((133, 28, 187, 292), radius=10, fill=color)
        d.ellipse((91, 91, 229, 229), fill="#aaaaaa")
        d.ellipse((101, 101, 219, 219), fill="#f8f8ed")
        d.line((160, 116, 160, 160, 195, 176), fill="#222222", width=5)
    elif kind == "phone":
        d.rounded_rectangle((99, 38, 224, 282), radius=22, fill=color, outline="#333333", width=3)
        for y in (65, 96):
            d.ellipse((112, y, 134, y+22), fill="#111111", outline="#999999", width=2)
        d.polygon([(164, 151), (171, 166), (187, 166), (174, 178), (179, 193), (164, 184), (150, 193), (154, 177), (142, 166), (159, 166)], fill="white")
    elif kind == "charger":
        d.rounded_rectangle((52, 107, 155, 219), radius=14, fill=color, outline="#aaaaaa", width=3)
        d.line((74, 106, 74, 82), fill="#888888", width=9)
        d.line((128, 106, 128, 82), fill="#888888", width=9)
        d.arc((125, 98, 283, 260), 270, 530, fill="#aaaaaa", width=9)
        d.line((203, 98, 235, 76), fill="#aaaaaa", width=9)
    elif kind == "glasses":
        d.ellipse((45, 121, 143, 216), outline=color, width=8)
        d.ellipse((177, 121, 275, 216), outline=color, width=8)
        d.arc((139, 143, 181, 174), 180, 350, fill=color, width=6)
        d.line((48, 149, 76, 72), fill=color, width=6)
        d.line((272, 149, 245, 72), fill=color, width=6)
    rotated = layer.rotate(rng.uniform(-12, 12), resample=Image.Resampling.BICUBIC)
    image.paste(rotated, mask=rotated.getchannel("A"))
    image.save(path)


def generate() -> dict:
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "images").mkdir(exist_ok=True)
    reports, pairs = [], {}
    for index, (name, category, lost, found, location, kind, color) in enumerate(EXAMPLES, 1):
        lost_id, found_id, negative_id = index, 100+index, 200+index
        pairs[str(lost_id)] = [found_id]
        for item_id, report_type, description, loc, day, variant in [
            (lost_id, "lost", lost, location, "2026-09-20", index),
            (found_id, "found", found, location, "2026-09-21", index+30),
            (negative_id, "found", lost, "Engineering Building" if index % 2 else location, "2026-08-02", index+60),
        ]:
            image_path = f"images/{item_id}.png"
            draw_fixture(kind, color, variant, DEST / image_path)
            reports.append(dict(id=item_id, report_type=report_type, name=name if report_type == "lost" else f"Found {kind}",
                                category="Bags" if item_id == 207 else category, description=description,
                                location=loc, location_detail="Near desk 14" if report_type == "found" else None,
                                identifying_details=description if report_type == "found" else None,
                                handover_location="Campus Security" if report_type == "found" else None,
                                event_date=day, image_path=image_path))
    for lost_id, found_id, name, category, lost, found, location in [
        (9, 109, "Red scarf", "Clothing", "Wool red scarf with white stripes", "Striped crimson wool neck warmer", "Student Services"),
        (10, 110, "Water bottle", "Water Bottles", "Steel blue bottle with a dent", "Dented blue metal flask", "Gym"),
    ]:
        pairs[str(lost_id)] = [found_id]
        for item_id, kind, description in [(lost_id, "lost", lost), (found_id, "found", found)]:
            reports.append(dict(id=item_id, report_type=kind, name=name, category=category, description=description,
                                location=location, location_detail=None,
                                identifying_details=description if kind == "found" else None,
                                handover_location="Student Services" if kind == "found" else None,
                                event_date=None if lost_id == 10 else "2026-09-22", image_path=None))
    data = {"provenance": "Entirely synthetic reports and procedural illustrations; not real-world evidence.",
            "seed": 100, "reports": reports, "relevant_pairs": pairs}
    (DEST / "reports.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


if __name__ == "__main__":
    data = generate()
    print(f"Generated {len(data['reports'])} synthetic reports and 24 illustrations in {DEST}")
