"""Labelled synthetic fixtures. Deterministic construction; no randomness or seed."""


def fixture():
    records = [{"id": f"p{i:02}", "kind": "person", "name": f"Synthetic Person {i:02}", "known": i < 10} for i in range(40)]
    records += [{"id": f"o{i:02}", "kind": "organisation", "name": f"Synthetic Organisation {i:02}", "target": i < 12} for i in range(20)]
    for i in range(20):
        records.append({"id": f"a{i:03}", "kind": "affiliation", "person_id": f"p{i:02}", "organisation_id": f"o{i % 10:02}", "role": "Synthetic member"})
    for i in range(80):
        records.append({"id": f"a{i + 20:03}", "kind": "affiliation", "person_id": f"p{20 + i // 4:02}", "organisation_id": f"o{12 + i % 4:02}", "role": "Synthetic member"})
    for i in range(40):
        start, end = (i, i + 10) if i < 10 else (20 + (i - 10) % 20, 20 + (i - 9) % 20)
        records.append({"id": f"c{i:03}", "kind": "connection", "from_id": f"p{start:02}", "to_id": f"p{end:02}"})
    return {"synthetic": True, "origin": "synthetic_fixture", "as_of": "2026-09-30", "records": records}


def expectations():
    """Independent hand arithmetic, never obtained by calling the engine."""
    return {"synthetic": True, "explanation": "40 people + 20 organisations + 100 affiliations + 40 connections = 200. Ten known people have one direct target affiliation each. Ten directed introductions reach ten other target affiliates. Targets o10 and o11 have no affiliations. Other affiliations and connections cannot start from a known person.",
            "counts": {"person_records": 40, "organisation_records": 20, "affiliation_records": 100,
                       "connection_records": 40, "records": 200, "known_contacts": 10,
                       "target_organisations": 12, "reachable_targets": 10, "unreachable_targets": 2,
                       "paths": 20, "direct_paths": 10, "one_intermediary_paths": 10},
            "path_keys": [[f"o{i:02}", [f"p{i:02}"]] for i in range(10)] +
                         [[f"o{i:02}", [f"p{i:02}", f"p{i + 10:02}"]] for i in range(10)],
            "unreachable_organisation_ids": ["o10", "o11"]}


def tiny_fixture():
    return {"synthetic": True, "origin": "synthetic_fixture", "as_of": "2026-09-30", "records": [
        {"id": "henry-contact", "kind": "person", "name": "Synthetic Contact", "known": True},
        {"id": "colleague", "kind": "person", "name": "Synthetic Colleague", "known": False},
        {"id": "target", "kind": "organisation", "name": "Synthetic Target", "target": True},
        {"id": "intro", "kind": "connection", "from_id": "henry-contact", "to_id": "colleague"},
        {"id": "job", "kind": "affiliation", "person_id": "colleague", "organisation_id": "target", "role": "Synthetic engineer"}]}
