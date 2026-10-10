import hashlib
import json
from pathlib import Path

import pytest

from scripts.evaluate_final_candidate import verify_freeze
from src.benchmark import load_split

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "data" / "benchmark" / "campus_v1"


def test_frozen_test_hashes_and_structure():
    config, manifest = verify_freeze()
    reports, qrels = load_split(BENCHMARK, "test")
    assert config["test_seed"] == manifest["seed"] == 9107
    assert len([item for item in reports if item.report_type == "lost"]) == len(qrels) == 16
    assert len([item for item in reports if item.report_type == "found"]) == 32


def test_dev_test_have_no_content_or_image_leakage():
    dev = json.loads((BENCHMARK / "dev" / "reports.json").read_text())["reports"]
    test = json.loads((BENCHMARK / "test" / "reports.json").read_text())["reports"]
    assert not ({item["id"] for item in dev} & {item["id"] for item in test})
    assert not ({item["description"] for item in dev} & {item["description"] for item in test})
    assert not ({item["identifying_details"] for item in dev if item["identifying_details"]} &
                {item["identifying_details"] for item in test if item["identifying_details"]})
    def hashes(split):
        return {hashlib.sha256(path.read_bytes()).hexdigest() for path in (BENCHMARK / split / "images").glob("*.png")}
    assert not (hashes("dev") & hashes("test"))


def test_frozen_generators_refuse_overwrite():
    from scripts.generate_benchmark import generate_dev
    from scripts.generate_final_test import main as generate_test
    from scripts.evaluate_final_candidate import main as evaluate_final
    with pytest.raises(RuntimeError, match="Frozen test split"):
        generate_dev()
    with pytest.raises(SystemExit, match="refusing to regenerate"):
        generate_test()
    with pytest.raises(SystemExit, match="refusing to rerun"):
        evaluate_final()
