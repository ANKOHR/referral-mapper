"""Pure validation and path computation. No inferred relationships or savings."""
from datetime import date


class SchemaError(ValueError):
    """An input field violates the documented schema."""


def _error(field, message):
    raise SchemaError(f"SchemaError: {field}: {message}")


def _string(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        _error(field, "expected nonempty string of at most 10000 characters")
    if any(ord(c) < 32 for c in value) or chr(0x2014) in value:
        _error(field, "control characters and U+2014 are forbidden")
    return value


def validate(data):
    if not isinstance(data, dict):
        _error("root", "expected object")
    required = {"synthetic", "origin", "as_of", "records"}
    if set(data) != required:
        _error("root", f"expected fields {sorted(required)}; differing fields {sorted(set(data) ^ required)}")
    if type(data["synthetic"]) is not bool:
        _error("synthetic", "expected boolean")
    expected_origin = "synthetic_fixture" if data["synthetic"] else "henry_hand_entered"
    if data["origin"] != expected_origin:
        _error("origin", f"expected {expected_origin}")
    try:
        as_of = date.fromisoformat(data["as_of"])
        if as_of.isoformat() != data["as_of"]:
            raise ValueError()
    except (TypeError, ValueError):
        _error("as_of", "expected YYYY-MM-DD")
    if not isinstance(data["records"], list):
        _error("records", "expected array")
    schemas = {
        "person": {"id", "kind", "name", "known"},
        "organisation": {"id", "kind", "name", "target"},
        "affiliation": {"id", "kind", "person_id", "organisation_id", "role"},
        "connection": {"id", "kind", "from_id", "to_id"},
    }
    ids = {}
    for index, record in enumerate(data["records"]):
        field = f"records[{index}]"
        if not isinstance(record, dict):
            _error(field, "expected object")
        kind = record.get("kind")
        if not isinstance(kind, str) or kind not in schemas:
            _error(field + ".kind", "unknown record kind")
        expected = schemas[kind]
        actual = set(record) - {"observed_on"}
        if actual != expected:
            _error(field, f"missing or unknown fields {sorted(actual ^ expected)}")
        for key in expected - {"known", "target"}:
            _string(record[key], field + "." + key)
        for key in expected & {"known", "target"}:
            if type(record[key]) is not bool:
                _error(field + "." + key, "expected boolean")
        if record["id"] in ids:
            _error(field + ".id", "duplicate id " + record["id"])
        ids[record["id"]] = kind
        if "observed_on" in record:
            try:
                observed = date.fromisoformat(record["observed_on"])
                if observed.isoformat() != record["observed_on"] or observed > as_of:
                    raise ValueError()
            except (TypeError, ValueError):
                _error(field + ".observed_on", "expected date on or before as_of")
    for index, record in enumerate(data["records"]):
        refs = {"affiliation": {"person_id": "person", "organisation_id": "organisation"},
                "connection": {"from_id": "person", "to_id": "person"}}.get(record["kind"], {})
        for key, kind in refs.items():
            if ids.get(record[key]) != kind:
                _error(f"records[{index}].{key}", f"expected existing {kind} id")
        if record["kind"] == "connection" and record["from_id"] == record["to_id"]:
            _error(f"records[{index}].to_id", "self connections are forbidden")
    return data


def compute(data):
    """Enumerate unique direct and one-intermediary paths; count explicit inputs."""
    validate(data)
    records = data["records"]
    people = {r["id"]: r for r in records if r["kind"] == "person"}
    organisations = {r["id"]: r for r in records if r["kind"] == "organisation"}
    known = sorted(p for p, r in people.items() if r["known"])
    targets = sorted(o for o, r in organisations.items() if r["target"])
    affiliations = {}
    for r in records:
        if r["kind"] == "affiliation":
            affiliations.setdefault((r["person_id"], r["organisation_id"]), []).append(r["id"])
    connections = {}
    for r in records:
        if r["kind"] == "connection":
            connections.setdefault((r["from_id"], r["to_id"]), []).append(r["id"])
    paths = []
    for target in targets:
        for start in known:
            for end in sorted(people):
                affiliation_ids = affiliations.get((end, target))
                if not affiliation_ids:
                    continue
                connection_ids = [] if start == end else connections.get((start, end))
                if connection_ids is None:
                    continue
                paths.append({"organisation_id": target, "organisation_name": organisations[target]["name"],
                              "person_ids": [start] if start == end else [start, end],
                              "person_names": [people[p]["name"] for p in ([start] if start == end else [start, end])],
                              "connection_record_ids": sorted(connection_ids),
                              "affiliation_record_ids": sorted(affiliation_ids),
                              "classification": "direct" if start == end else "one_intermediary"})
    reached = {p["organisation_id"] for p in paths}
    counts = {kind + "_records": sum(r["kind"] == kind for r in records)
              for kind in ("person", "organisation", "affiliation", "connection")}
    counts.update({"records": len(records), "known_contacts": len(known), "target_organisations": len(targets),
                   "reachable_targets": len(reached), "unreachable_targets": len(targets) - len(reached),
                   "paths": len(paths), "direct_paths": sum(p["classification"] == "direct" for p in paths),
                   "one_intermediary_paths": sum(p["classification"] == "one_intermediary" for p in paths)})
    return {"schema_version": 1, "as_of": data["as_of"], "synthetic": data["synthetic"],
            "origin": data["origin"], "counts": counts, "paths": paths,
            "unreachable_organisation_ids": sorted(set(targets) - reached),
            "limitations": "Possible paths from supplied records only. Willingness, current relationships, conversion, time saved and money saved are unmeasured."}
