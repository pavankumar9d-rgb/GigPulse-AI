"""Unit and integration tests for the deterministic synthetic data generator."""

import json
from pathlib import Path
import pytest
from gigpulse_core.synthetic_generator import SyntheticDataGenerator
from gigpulse_core.validator import validate_csv_content


def test_synthetic_data_generation_and_validation(tmp_path: Path):
    generator = SyntheticDataGenerator(seed=42, num_weeks=2)
    manifest = generator.generate_all(tmp_path)

    assert manifest["project"] == "GigPulse AI"
    assert manifest["synthetic"] is True
    assert manifest["seed"] == 42
    assert manifest["counts"]["work_sessions"] > 0
    assert manifest["counts"]["deliveries"] > 0
    assert manifest["counts"]["expenses"] > 0
    assert manifest["counts"]["zone_demand_observations"] > 0

    # Verify manifest file on disk
    manifest_file = tmp_path / "dataset_manifest.json"
    assert manifest_file.exists()
    with open(manifest_file, "r", encoding="utf-8") as f:
        disk_manifest = json.load(f)
    assert disk_manifest["synthetic"] is True

    # Check each CSV file exists and passes validation 100%
    csv_templates = ["work_sessions", "deliveries", "expenses", "zone_demand"]
    for t_key in csv_templates:
        csv_file = tmp_path / f"{t_key}.csv"
        assert csv_file.exists()

        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()

        report = validate_csv_content(content, t_key)
        assert report.is_valid, f"{t_key}.csv failed validation: {[e.error_message for e in report.errors]}"
        assert report.rejected_rows == 0
        assert report.accepted_rows == manifest["counts"][t_key] if t_key in manifest["counts"] else report.accepted_rows > 0

        # Check that 100% of records carry source_type='synthetic' and target_quality='synthetic'
        for rec in report.valid_records:
            assert rec.source_type == "synthetic"
            if hasattr(rec, "target_quality"):
                assert rec.target_quality == "synthetic"


def test_generator_determinism(tmp_path: Path):
    path_a = tmp_path / "run_a"
    path_b = tmp_path / "run_b"

    gen_a = SyntheticDataGenerator(seed=123, num_weeks=1)
    gen_b = SyntheticDataGenerator(seed=123, num_weeks=1)

    gen_a.generate_all(path_a)
    gen_b.generate_all(path_b)

    # All generated files must be byte-for-byte identical
    for filename in ["work_sessions.csv", "deliveries.csv", "expenses.csv", "zone_demand.csv"]:
        content_a = (path_a / filename).read_text(encoding="utf-8")
        content_b = (path_b / filename).read_text(encoding="utf-8")
        assert content_a == content_b, f"{filename} differed across identical seed runs"

