# Referral Mapper

Referral Mapper computes possible warm paths to target organisations from explicit local records. It does not discover contacts, infer relationships, predict introductions, or call a language model. It uses Python's standard library, CPU only, and makes no network calls.

Hypothesis: a deterministic CLI with tested, explicit relationship records gives Henry a trustworthy way to inspect potential introductions. Synthetic acceptance tests validate the computation. They do not validate demand, current relationships, willingness to introduce, or outreach outcomes.

## Quickstart

Python 3.10 or later and setuptools are required. From this directory:

```powershell
python -m pip install --no-index --disable-pip-version-check --no-deps --no-build-isolation -e .
python -m referral_mapper.cli fixtures --out demo
python -m referral_mapper.cli run --input demo
python -m referral_mapper.cli report --format md
python -m pytest -q
```

The installed executable is `rm`. If its Scripts directory is not on PATH, use the module commands above or the full path printed by pip. In PowerShell, `rm` is normally an alias for `Remove-Item`. Use `rm.exe` or `python -m referral_mapper.cli` to avoid that alias. In shells without that alias, the required demo is:

```sh
rm fixtures --out demo && rm run --input demo && rm report --format md
```

For the smallest hand-written five-record example, add `--tiny` to fixtures. Checked-in examples live in `examples/tiny` and `examples/synthetic-200`. The default generated set has exactly 200 records. Reports use the last successful run, stored in `.referral-mapper/results.json`, not the expectations file. A failed run leaves the previous state intact, so check its exit code before reporting.

## Input format

The input directory contains one UTF-8 `dataset.json` file. JSON does not allow comments. `expectations.json` and `LABEL.md` are fixture documentation, never computation inputs. Other files alongside dataset.json are not parsed. CSV and YAML are not supported; convert them to this schema first. An empty directory is valid and gives zero counts with a NO INPUTS provenance banner. A missing directory is an error.

```json
{
  "synthetic": false,
  "origin": "henry_hand_entered",
  "as_of": "2026-09-30",
  "records": [
    {"id": "friend", "kind": "person", "name": "Contact entered by Henry", "known": true},
    {"id": "firm", "kind": "organisation", "name": "Target entered by Henry", "target": true},
    {"id": "job", "kind": "affiliation", "person_id": "friend", "organisation_id": "firm", "role": "Engineer"}
  ]
}
```

This snippet illustrates the schema, not a measured real relationship. Only label inputs real when Henry actually supplies his own records. The tool reports the declaration and cannot independently verify it. Synthetic inputs must instead use `synthetic: true` and `origin: "synthetic_fixture"`. A dataset has one provenance class; mixed real and synthetic datasets are not supported and must be separated.

| Record kind | Required fields |
| --- | --- |
| person | id, kind, name, known (boolean) |
| organisation | id, kind, name, target (boolean) |
| affiliation | id, kind, person_id, organisation_id, role |
| connection | id, kind, from_id, to_id |

Every record can additionally carry `observed_on`, an ISO date on or before the explicit dataset `as_of`. Dates are validated against that input cutoff, never the machine clock. Choosing a later as_of is an explicit user assertion, not a tool forecast. Unknown fields, including monetary amounts, are rejected rather than ignored. Negative amounts therefore cause a SchemaError. Global record ids must be unique. References must exist and have the correct kind. Self connections are rejected. All strings must be nonempty, at most 10,000 characters, and contain neither control characters nor U+2014. Unicode and literal Windows paths are supported; escape backslashes in JSON. Duplicate JSON field names are rejected.

A `known` person is someone Henry declares he can approach. A directed `connection` means the from person has an explicitly recorded possible introduction to the to person. Reversing an edge changes its meaning. An `affiliation` connects a person to an organisation; role is supporting context, not a score.

For each target, the engine enumerates:

1. Direct: known person -> target organisation, using an affiliation.
2. One intermediary: known person -> person -> target organisation, using a directed connection and affiliation.

Longer chains are excluded. No relationship is inferred from matching names. Identity depends only on ids, with case-sensitive exact matching. Paths are unique by target id and ordered person ids. Repeated relationships with distinct record ids retain all evidence ids on one path; raw record totals still include each record. Roles remain available in source records referenced by the path's evidence ids. A target with no such path is unreachable within this bounded input graph, not necessarily in reality.

## Subcommands

Every subcommand supports `--help` with an example.

| Command | Purpose and example |
| --- | --- |
| fixtures | `rm fixtures --out demo` generates 200 labelled records; `--tiny` generates five |
| run | `rm run --input demo --state local-results.json` validates, computes, atomically saves |
| report | `rm report --format json --state local-results.json --output report.json` renders saved results |
| validate | `rm validate --input demo` checks fields, dates, ids and references without saving |
| paths | `rm paths --target o00 --state local-results.json` lists bounded paths to that id |

Default report format is Markdown. An unknown target in `paths` returns an empty list; this is an exact id filter, not a search or discovery feature. All path output includes provenance and unmeasured-outcome wording. Exit code 0 means success; 2 means a named input, schema, usage, state, or write error.

## Architecture

```text
fixtures.py -> labelled dataset.json + independent expectations.json
                           |
cli.py: local file parsing + named errors + atomic writes
                           |
core.py: schema validation -> directed bounded paths -> exact counts
                           |
.referral-mapper/results.json -> report.py -> Markdown / JSON
```

Core functions contain no I/O. Rendering sorts fields and computation sorts ids. Fixture construction uses fixed loops and no randomness, so no random seed is needed. There are no timestamps or measured durations inside deterministic result files. The same input and settings yield byte-identical saved state and reports, including on Windows (UTF-8 with LF newlines). Paths in input strings are data, never opened or executed. Inputs are never modified by run or validate.

## Honesty boundary and fixture labels

Reports distinguish synthetic fixtures, declared Henry-entered real data, and empty inputs. Only exact input counts and paths are computed. Time saved, money saved, conversion, relationship freshness, introduction willingness, and real-world accuracy are unmeasured. No savings or hypothetical numerical business outcomes are emitted. An illustrative schema example is explicitly labelled above. Synthetic acceptance is not evidence of paid demand.

Every fixture JSON has a root `synthetic: true` field. JSON cannot carry header comments; every accompanying Markdown label has `<!-- synthetic: true -->` as its header comment. Both the 200-record expectations and input files are synthetic. Report banners repeat the label. No real contacts or trial data ship in this repository.

## Acceptance evidence

The independent hand calculation is in each 200-record `expectations.json`. Forty people plus twenty organisations plus one hundred affiliations plus forty connections total two hundred. Ten known contacts each yield one direct path and one introduction path, giving twenty distinct paths to ten targets. Two additional targets are unreachable. Eight organisations are not targets. No paths should arise from the eighty non-target affiliations or thirty connections among unknown people.

Tests compare every count and every path id tuple, proving all planted cases found and zero false positives on this fixture. Corrupting a known-contact flag removes its two paths and its reachable target, proving results are computed. Tests also cover malformed JSON, strict schemas, future observation dates, duplicate ids, Unicode, long strings, directed edges, byte identity, empty input, write failures and CLI help.

`EVIDENCE.json` records the measured local full demo duration and test run. `BUILD-DONE.txt` identifies the implementation commit and build summary. Timing is machine-specific measured fixture performance, not time saved against a workflow baseline.

## Failure modes

- Malformed JSON: ParseError includes file and JSON parser line. Unsupported formats receive a named schema error with file and line 1. No traceback.
- Missing input: MissingInput includes directory and fixtures usage hint.
- Schema drift: SchemaError includes offending fields and source filename; record locations use array indexes.
- Bad report output path: WriteError. Temp files are cleaned up; an existing destination is preserved if replacement fails. Individual writes are atomic; multi-file fixture generation is not a transaction.
- Missing or invalid saved state: MissingResult or SchemaError with rerun hint. Saved state is local generated output, not a substitute for a validated input dataset.
- Stale, false or omitted relationships: cannot be detected from graph structure. A hand-check against Henry's records is required. No source freshness or relationship likelihood claim is made.
- Large graphs: direct and one-intermediary enumeration may yield many paths; performance acceptance applies to the 200-record fixture only. Files are read into memory.

## Two-week improvement hook and verdict

The trial starts on Henry's first real use, not on this build date. Keep real trial data outside the repository. For fourteen days, record actual run dates and hand-check a sample of reported paths against source relationships. Use `TRIAL-TEMPLATE.md` to record sample size, incorrect paths, error rate (incorrect / checked), missing paths discovered during review, and run count. With zero checked paths the error rate is unmeasured, never zero. A measured error rate above 10 percent triggers fixing the largest observed cause or killing the project. Zero actual use triggers kill with a recorded reason. Missing-path evidence also informs that diagnosis. Time savings are optional and require a timed manual baseline on the same input.

No two-week real-use evidence exists at build completion. Final verdict is pending that window, explicitly not invented. Record the verdict and reason in a local trial record: expand for daily use or revenue; integrate for strong sibling overlap; commercialise if a buyer would pay as-is; maintain for portfolio evidence otherwise; kill for non-use or inability to meet acceptance. The synthetic build currently meets local computational acceptance; that is not a commercial verdict.
