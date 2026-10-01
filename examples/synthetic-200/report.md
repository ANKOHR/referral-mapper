<!-- synthetic: true -->
# Referral Mapper

Data provenance: SYNTHETIC fixtures only; no real inputs.

As of: 2026-09-30

Input files: ["dataset.json"]

Possible paths from supplied records only. Willingness, current relationships, conversion, time saved and money saved are unmeasured.

All counts are computed from supplied inputs. Synthetic results demonstrate computation, not real-world accuracy.

## Computed counts

- affiliation_records: 100
- connection_records: 40
- direct_paths: 10
- known_contacts: 10
- one_intermediary_paths: 10
- organisation_records: 20
- paths: 20
- person_records: 40
- reachable_targets: 10
- records: 200
- target_organisations: 12
- unreachable_targets: 2

## Possible paths

- {"affiliation_record_ids": ["a000"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o00", "organisation_name": "Synthetic Organisation 00", "person_ids": ["p00"], "person_names": ["Synthetic Person 00"]}
- {"affiliation_record_ids": ["a010"], "classification": "one_intermediary", "connection_record_ids": ["c000"], "organisation_id": "o00", "organisation_name": "Synthetic Organisation 00", "person_ids": ["p00", "p10"], "person_names": ["Synthetic Person 00", "Synthetic Person 10"]}
- {"affiliation_record_ids": ["a001"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o01", "organisation_name": "Synthetic Organisation 01", "person_ids": ["p01"], "person_names": ["Synthetic Person 01"]}
- {"affiliation_record_ids": ["a011"], "classification": "one_intermediary", "connection_record_ids": ["c001"], "organisation_id": "o01", "organisation_name": "Synthetic Organisation 01", "person_ids": ["p01", "p11"], "person_names": ["Synthetic Person 01", "Synthetic Person 11"]}
- {"affiliation_record_ids": ["a002"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o02", "organisation_name": "Synthetic Organisation 02", "person_ids": ["p02"], "person_names": ["Synthetic Person 02"]}
- {"affiliation_record_ids": ["a012"], "classification": "one_intermediary", "connection_record_ids": ["c002"], "organisation_id": "o02", "organisation_name": "Synthetic Organisation 02", "person_ids": ["p02", "p12"], "person_names": ["Synthetic Person 02", "Synthetic Person 12"]}
- {"affiliation_record_ids": ["a003"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o03", "organisation_name": "Synthetic Organisation 03", "person_ids": ["p03"], "person_names": ["Synthetic Person 03"]}
- {"affiliation_record_ids": ["a013"], "classification": "one_intermediary", "connection_record_ids": ["c003"], "organisation_id": "o03", "organisation_name": "Synthetic Organisation 03", "person_ids": ["p03", "p13"], "person_names": ["Synthetic Person 03", "Synthetic Person 13"]}
- {"affiliation_record_ids": ["a004"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o04", "organisation_name": "Synthetic Organisation 04", "person_ids": ["p04"], "person_names": ["Synthetic Person 04"]}
- {"affiliation_record_ids": ["a014"], "classification": "one_intermediary", "connection_record_ids": ["c004"], "organisation_id": "o04", "organisation_name": "Synthetic Organisation 04", "person_ids": ["p04", "p14"], "person_names": ["Synthetic Person 04", "Synthetic Person 14"]}
- {"affiliation_record_ids": ["a005"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o05", "organisation_name": "Synthetic Organisation 05", "person_ids": ["p05"], "person_names": ["Synthetic Person 05"]}
- {"affiliation_record_ids": ["a015"], "classification": "one_intermediary", "connection_record_ids": ["c005"], "organisation_id": "o05", "organisation_name": "Synthetic Organisation 05", "person_ids": ["p05", "p15"], "person_names": ["Synthetic Person 05", "Synthetic Person 15"]}
- {"affiliation_record_ids": ["a006"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o06", "organisation_name": "Synthetic Organisation 06", "person_ids": ["p06"], "person_names": ["Synthetic Person 06"]}
- {"affiliation_record_ids": ["a016"], "classification": "one_intermediary", "connection_record_ids": ["c006"], "organisation_id": "o06", "organisation_name": "Synthetic Organisation 06", "person_ids": ["p06", "p16"], "person_names": ["Synthetic Person 06", "Synthetic Person 16"]}
- {"affiliation_record_ids": ["a007"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o07", "organisation_name": "Synthetic Organisation 07", "person_ids": ["p07"], "person_names": ["Synthetic Person 07"]}
- {"affiliation_record_ids": ["a017"], "classification": "one_intermediary", "connection_record_ids": ["c007"], "organisation_id": "o07", "organisation_name": "Synthetic Organisation 07", "person_ids": ["p07", "p17"], "person_names": ["Synthetic Person 07", "Synthetic Person 17"]}
- {"affiliation_record_ids": ["a008"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o08", "organisation_name": "Synthetic Organisation 08", "person_ids": ["p08"], "person_names": ["Synthetic Person 08"]}
- {"affiliation_record_ids": ["a018"], "classification": "one_intermediary", "connection_record_ids": ["c008"], "organisation_id": "o08", "organisation_name": "Synthetic Organisation 08", "person_ids": ["p08", "p18"], "person_names": ["Synthetic Person 08", "Synthetic Person 18"]}
- {"affiliation_record_ids": ["a009"], "classification": "direct", "connection_record_ids": [], "organisation_id": "o09", "organisation_name": "Synthetic Organisation 09", "person_ids": ["p09"], "person_names": ["Synthetic Person 09"]}
- {"affiliation_record_ids": ["a019"], "classification": "one_intermediary", "connection_record_ids": ["c009"], "organisation_id": "o09", "organisation_name": "Synthetic Organisation 09", "person_ids": ["p09", "p19"], "person_names": ["Synthetic Person 09", "Synthetic Person 19"]}

Unreachable target ids: ["o10", "o11"]
