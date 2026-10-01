"""Local-only CLI. Use python -m referral_mapper.cli on Windows if rm is aliased."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import SchemaError, compute
from .fixtures import fixture, expectations, tiny_fixture
from .report import banner, json_text, render


class InputError(ValueError):
    """Named input error suitable for CLI output."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field {key}")
        result[key] = value
    return result


def load_input(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}: expected input directory; use rm fixtures --out demo")
    path = directory / "dataset.json"
    if not path.exists():
        extras = sorted(p for p in directory.iterdir() if p.is_file())
        if extras:
            raise InputError(f"SchemaError: {extras[0]}: line 1: expected dataset.json; unsupported input file")
        return {"synthetic": False, "origin": "henry_hand_entered", "as_of": "2026-09-30", "records": []}
    try:
        raw = path.read_text(encoding="utf-8-sig")
        value = json.loads(raw, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise InputError(f"ParseError: {path}: line {exc.lineno}: {exc.msg}") from exc
    except (OSError, UnicodeError, ValueError) as exc:
        raise InputError(f"ParseError: {path}: line 1: {exc}") from exc
    try:
        compute(value)
    except SchemaError as exc:
        # Schema diagnostics identify a logical field as well as the source file.
        raise InputError(f"{exc}: file {path}: line 1 (field location shown above)") from exc
    return value


def atomic_write(path, content):
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc}") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def read_result(path):
    try:
        result = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"MissingResult: {path}: run rm run --input <dir> first; {exc}") from exc
    if not isinstance(result, dict) or result.get("schema_version") != 1 or not all(k in result for k in ("counts", "paths", "synthetic", "limitations", "as_of", "unreachable_organisation_ids")):
        raise InputError(f"SchemaError: {path}: invalid result schema; rerun rm run")
    def bad_state():
        raise InputError(f"SchemaError: {path}: invalid result fields; rerun rm run")
    if (type(result["synthetic"]) is not bool or not isinstance(result["counts"], dict)
            or not all(isinstance(k, str) and type(v) is int and v >= 0 for k, v in result["counts"].items())
            or not isinstance(result["paths"], list)
            or not isinstance(result["limitations"], str) or not isinstance(result["as_of"], str)
            or not isinstance(result["unreachable_organisation_ids"], list)):
        bad_state()
    for item in result["paths"]:
        required = {"organisation_id", "organisation_name", "person_ids", "person_names",
                    "connection_record_ids", "affiliation_record_ids", "classification"}
        if not isinstance(item, dict) or set(item) != required:
            bad_state()
        for field in ("organisation_id", "organisation_name", "classification"):
            if not isinstance(item[field], str):
                bad_state()
        for field in ("person_ids", "person_names", "connection_record_ids", "affiliation_record_ids"):
            if not isinstance(item[field], list) or not all(isinstance(value, str) for value in item[field]):
                bad_state()
    return result


def parser():
    root = argparse.ArgumentParser(description="Compute possible warm paths from explicit local records. No discovery or prediction.")
    sub = root.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fixtures", help="Generate labelled synthetic inputs", epilog="Example: rm fixtures --out demo")
    f.add_argument("--out", required=True)
    f.add_argument("--tiny", action="store_true", help="Generate the hand-written five-record fixture")
    for name in ("run", "validate"):
        p = sub.add_parser(name, help="Compute and save paths" if name == "run" else "Validate all records and references", epilog=f"Example: rm {name} --input demo")
        p.add_argument("--input", required=True)
        if name == "run":
            p.add_argument("--state", default=".referral-mapper/results.json")
    r = sub.add_parser("report", help="Render computed results with provenance", epilog="Example: rm report --format md")
    r.add_argument("--format", choices=["md", "json"], default="md")
    r.add_argument("--state", default=".referral-mapper/results.json")
    r.add_argument("--output", help="Atomically write report to a local file")
    p = sub.add_parser("paths", help="Inspect possible paths to one explicit target id", epilog="Example: rm paths --target o00")
    p.add_argument("--target", required=True)
    p.add_argument("--state", default=".referral-mapper/results.json")
    return root


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    try:
        if args.command == "fixtures":
            data = tiny_fixture() if args.tiny else fixture()
            atomic_write(Path(args.out) / "dataset.json", json_text(data))
            if not args.tiny:
                atomic_write(Path(args.out) / "expectations.json", json_text(expectations()))
            atomic_write(Path(args.out) / "LABEL.md", "<!-- synthetic: true -->\nSynthetic fixture only. No real contacts or organisations.\n")
            print(f"SYNTHETIC fixture: {len(data['records'])} records written to {args.out}")
        elif args.command in ("run", "validate"):
            data = load_input(args.input)
            result = compute(data)
            result["input_files"] = ["dataset.json"] if (Path(args.input) / "dataset.json").exists() else []
            if not result["input_files"]:
                result["empty_input"] = True
            if args.command == "run":
                atomic_write(args.state, json_text(result))
            print(banner(result))
            print(f"{args.command}: {result['counts']['records']} records; {result['counts']['paths']} possible paths. Outcomes and savings are unmeasured.")
        else:
            result = read_result(args.state)
            if args.command == "paths":
                selected = [p for p in result["paths"] if p["organisation_id"] == args.target]
                print(json_text({"provenance_banner": banner(result), "target_id": args.target, "paths": selected, "limitations": result["limitations"]}), end="")
            else:
                content = render(result, args.format)
                if args.output:
                    atomic_write(args.output, content)
                else:
                    print(content, end="")
        return 0
    except (InputError, SchemaError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"FileError: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
