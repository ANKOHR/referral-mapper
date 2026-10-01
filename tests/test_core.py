from copy import deepcopy
import pytest
from referral_mapper.core import compute, SchemaError
from referral_mapper.fixtures import fixture, tiny_fixture


def test_directed_and_bounded_paths():
    data = tiny_fixture()
    assert compute(data)["counts"]["one_intermediary_paths"] == 1
    data["records"][3]["from_id"], data["records"][3]["to_id"] = "colleague", "henry-contact"
    assert compute(data)["paths"] == []


@pytest.mark.parametrize("mutation,field", [
    (lambda d: d["records"].append(deepcopy(d["records"][0])), "id"),
    (lambda d: d["records"][0].update(amount=-1), "amount"),
    (lambda d: d["records"][0].update(observed_on="2026-10-01"), "observed_on"),
    (lambda d: d["records"][0].update(name="x" * 10001), "name"),
    (lambda d: d["records"][0].update(known=1), "known"),
    (lambda d: d["records"][3].update(to_id="missing"), "to_id"),
    (lambda d: d["records"][3].update(to_id="henry-contact"), "to_id"),
    (lambda d: d.update(synthetic="true"), "synthetic"),
    (lambda d: d.update(origin="invented"), "origin"),
    (lambda d: d["records"][0].update(name="bad" + chr(0x2014)), "name"),
    (lambda d: d["records"][0].update(name="bad\nname"), "name"),
    (lambda d: d.update(as_of="bad"), "as_of"),
    (lambda d: d["records"][0].update(kind=[]), "kind"),
])
def test_rejects_adversarial_values(mutation, field):
    data = tiny_fixture()
    mutation(data)
    with pytest.raises(SchemaError, match=field):
        compute(data)


def test_handles_unicode_and_long_inputs():
    data = tiny_fixture()
    data["records"][0]["name"] = "李 Zoë " + "x" * 9000 + r" C:\Users\henry\contacts"
    assert compute(data)["paths"][0]["person_names"][0] == data["records"][0]["name"]


def test_duplicate_edges_reconcile_without_duplicate_paths():
    data = tiny_fixture()
    data["records"].append({**data["records"][3], "id": "second-intro"})
    result = compute(data)
    assert result["counts"]["connection_records"] == 2
    assert result["counts"]["paths"] == 1
    assert result["paths"][0]["connection_record_ids"] == ["intro", "second-intro"]


def test_corrupted_fixture_changes_output():
    data = fixture()
    before = compute(data)
    data["records"][0]["known"] = False
    after = compute(data)
    assert before["counts"]["paths"] == 20
    assert after["counts"]["paths"] == 18
    assert after["counts"]["reachable_targets"] == 9


def test_input_order_does_not_change_result():
    data = fixture()
    original = compute(data)
    data["records"].reverse()
    assert compute(data) == original
