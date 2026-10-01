import json
from referral_mapper.cli import main
from referral_mapper.core import compute
from referral_mapper.fixtures import fixture, expectations, tiny_fixture


def test_fixtures_labelled_synthetic(tmp_path):
    assert main(["fixtures", "--out", str(tmp_path)]) == 0
    for path in tmp_path.iterdir():
        if path.suffix == ".json":
            assert json.loads(path.read_text(encoding="utf-8"))["synthetic"] is True
        else:
            assert "<!-- synthetic: true -->" in path.read_text()


def test_fixture_ground_truth_matches_hand_computed():
    actual, expected = compute(fixture()), expectations()
    assert len(fixture()["records"]) == 200
    assert actual["counts"] == expected["counts"]
    assert sorted((p["organisation_id"], p["person_ids"]) for p in actual["paths"]) == sorted((o, people) for o, people in expected["path_keys"])
    assert actual["unreachable_organisation_ids"] == expected["unreachable_organisation_ids"]


def test_tiny_hand_written_fixture():
    result = compute(tiny_fixture())
    assert result["counts"]["records"] == 5
    assert result["paths"][0]["person_ids"] == ["henry-contact", "colleague"]
