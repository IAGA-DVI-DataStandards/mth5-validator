from __future__ import annotations

import sys
from pathlib import Path

import h5py

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mth5_validator_standalone import MTH5Validator


def _metadata_codes(results):
    return [
        msg.details.get("code")
        for msg in results.messages
        if msg.category == "Metadata" and "code" in msg.details
    ]


def _build_minimal_v02_file(file_path: Path, with_node_metadata: bool = True) -> None:
    with h5py.File(file_path, "w") as h5:
        h5.attrs["file.type"] = "MTH5"
        h5.attrs["file.version"] = "0.2.0"
        h5.attrs["data_level"] = 1

        experiment = h5.create_group("Experiment")
        surveys = experiment.create_group("Surveys")
        experiment.create_group("Reports")
        experiment.create_group("Standards")
        experiment.create_dataset("channel_summary", data=[1])
        experiment.create_dataset("tf_summary", data=[1])

        survey = surveys.create_group("survey_a")
        stations = survey.create_group("Stations")
        survey.create_group("Reports")
        survey.create_group("Filters")
        survey.create_group("Standards")

        station = stations.create_group("station_a")
        run = station.create_group("run_a")
        channel = run.create_dataset("hx", data=[0.1, 0.2, 0.3])

        if with_node_metadata:
            experiment.attrs["mth5_type"] = "survey"
            survey.attrs["mth5_type"] = "survey"
            station.attrs["mth5_type"] = "station"
            run.attrs["mth5_type"] = "run"
            channel.attrs["mth5_type"] = "channel"


def test_quick_metadata_reports_missing_required_root_key(tmp_path):
    file_path = tmp_path / "missing_root_metadata.mth5"
    with h5py.File(file_path, "w") as h5:
        h5.attrs["file.type"] = "MTH5"
        h5.create_group("Experiment")

    results = MTH5Validator(
        file_path,
        check_metadata=True,
        metadata_level="quick",
    ).validate()

    codes = _metadata_codes(results)
    assert "META_MISSING_REQUIRED" in codes


def test_full_metadata_checks_ranges_and_cross_field_consistency(tmp_path):
    file_path = tmp_path / "full_metadata_checks.mth5"
    _build_minimal_v02_file(file_path, with_node_metadata=True)

    with h5py.File(file_path, "a") as h5:
        survey = h5["/Experiment/Surveys/survey_a"]
        run = h5["/Experiment/Surveys/survey_a/Stations/station_a/run_a"]
        channel = h5["/Experiment/Surveys/survey_a/Stations/station_a/run_a/hx"]

        survey.attrs["latitude"] = 120.0
        run.attrs["time_period.start"] = "2026-01-02T00:00:00"
        run.attrs["time_period.end"] = "2026-01-01T00:00:00"
        channel.attrs["sample_rate"] = -1.0

    results = MTH5Validator(
        file_path,
        check_metadata=True,
        metadata_level="full",
    ).validate()

    codes = _metadata_codes(results)
    assert "META_RANGE_INVALID" in codes
    assert "META_CROSS_FIELD_INVALID" in codes


def test_quick_metadata_does_not_run_full_range_checks(tmp_path):
    file_path = tmp_path / "quick_no_full_checks.mth5"
    _build_minimal_v02_file(file_path, with_node_metadata=True)

    with h5py.File(file_path, "a") as h5:
        survey = h5["/Experiment/Surveys/survey_a"]
        survey.attrs["latitude"] = 120.0

    results = MTH5Validator(
        file_path,
        check_metadata=True,
        metadata_level="quick",
    ).validate()

    codes = _metadata_codes(results)
    assert "META_RANGE_INVALID" not in codes


def test_full_metadata_respects_max_errors_limit(tmp_path):
    file_path = tmp_path / "max_errors_stop.mth5"
    _build_minimal_v02_file(file_path, with_node_metadata=False)

    results = MTH5Validator(
        file_path,
        check_metadata=True,
        metadata_level="full",
        max_errors=2,
    ).validate()

    codes = _metadata_codes(results)
    assert "META_MAX_ERRORS_REACHED" in codes
    assert results.error_count <= 2
