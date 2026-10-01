import json
import pytest
from referral_mapper.core import compute
from referral_mapper.fixtures import fixture, expectations
from referral_mapper.report import render


def test_report_matches_ground_truth_exact():
    result = json.loads(render(compute(fixture()), "json"))
    assert result["counts"] == expectations()["counts"]
    md = render(compute(fixture()))
    for key, count in expectations()["counts"].items():
        assert f"- {key}: {count}\n" in md


def test_report_zero_false_positives():
    paths = json.loads(render(compute(fixture()), "json"))["paths"]
    observed = {(p["organisation_id"], tuple(p["person_ids"])) for p in paths}
    expected = {(o, tuple(people)) for o, people in expectations()["path_keys"]}
    assert observed - expected == set()
    assert expected - observed == set()
    assert len(paths) == len(expected)


@pytest.mark.parametrize("format", ["md", "json"])
def test_report_carries_provenance_banner(format):
    data = fixture()
    assert "SYNTHETIC fixtures only; no real inputs" in render(compute(data), format)
    data.update(synthetic=False, origin="henry_hand_entered")
    assert "Henry's own hand-entered data" in render(compute(data), format)
    assert "not independently verified" in render(compute(data), format)


def test_hypothetical_figures_labelled():
    report = render(compute(fixture()))
    assert "time saved and money saved are unmeasured" in report
    assert "not real-world accuracy" in report
    assert not any(key in compute(fixture())["counts"] for key in ("money_saved", "time_saved", "conversion_rate"))


def test_no_em_dashes_in_outputs():
    for format in ("md", "json"):
        assert chr(0x2014) not in render(compute(fixture()), format)
