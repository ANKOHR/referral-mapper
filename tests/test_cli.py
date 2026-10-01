import json
import os
from pathlib import Path
import subprocess
import sys
import time
from referral_mapper.cli import main, atomic_write, InputError
from referral_mapper.report import json_text
import pytest


def setup_fixture(tmp_path):
    directory = tmp_path / "inputs"
    state = tmp_path / "state.json"
    assert main(["fixtures", "--out", str(directory)]) == 0
    return directory, state


def test_run_completes_on_fixture(tmp_path):
    directory, state = setup_fixture(tmp_path)
    started = time.perf_counter()
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
    assert main(["report", "--state", str(state)]) == 0
    assert time.perf_counter() - started < 5


def test_empty_input_renders_without_traceback(tmp_path, capsys):
    state = tmp_path / "result.json"
    assert main(["run", "--input", str(tmp_path), "--state", str(state)]) == 0
    assert main(["report", "--state", str(state)]) == 0
    output = capsys.readouterr().out
    assert "NO INPUTS" in output
    assert "records: 0" in output
    assert "Traceback" not in output


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / "dataset.json").write_text('{\n"broken": }', encoding="utf-8")
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and "dataset.json" in error and "line 2" in error
    assert "Traceback" not in error


def test_missing_input_named_error(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "missing")]) == 2
    assert "MissingInput" in capsys.readouterr().err


def test_schema_error_names_file_and_field(tmp_path, capsys):
    directory, state = setup_fixture(tmp_path)
    path = directory / "dataset.json"
    data = json.loads(path.read_text())
    data["records"][0]["known"] = -1
    path.write_text(json_text(data), encoding="utf-8")
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 2
    error = capsys.readouterr().err
    assert "SchemaError" in error and "known" in error and "dataset.json" in error
    assert not state.exists()


def test_determinism_byte_identical(tmp_path):
    directory, state = setup_fixture(tmp_path)
    output = tmp_path / "report.md"
    def run():
        assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
        assert main(["report", "--state", str(state), "--output", str(output)]) == 0
        return state.read_bytes(), output.read_bytes()
    assert run() == run()
    original = (directory / "dataset.json").read_bytes()
    assert main(["fixtures", "--out", str(directory)]) == 0
    assert (directory / "dataset.json").read_bytes() == original


def test_cli_smoke_all_subcommands(tmp_path, capsys):
    directory, state = setup_fixture(tmp_path)
    assert main(["validate", "--input", str(directory)]) == 0
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
    assert main(["paths", "--target", "o00", "--state", str(state)]) == 0
    assert main(["report", "--format", "json", "--state", str(state)]) == 0
    assert chr(0x2014) not in capsys.readouterr().out
    for command in ("fixtures", "run", "validate", "paths", "report"):
        process = subprocess.run([sys.executable, "-m", "referral_mapper.cli", command, "--help"], capture_output=True, text=True)
        assert process.returncode == 0
        assert "Example:" in process.stdout


def test_report_write_failure_no_partial_files(tmp_path, capsys):
    directory, state = setup_fixture(tmp_path)
    main(["run", "--input", str(directory), "--state", str(state)])
    blocked = tmp_path / "blocked"
    blocked.write_text("keep")
    assert main(["report", "--state", str(state), "--output", str(blocked / "report.md")]) == 2
    assert "WriteError" in capsys.readouterr().err
    assert blocked.read_text() == "keep"
    assert not list(tmp_path.glob("tmp*"))


def test_atomic_replace_failure_preserves_existing_file(tmp_path, monkeypatch):
    output = tmp_path / "report.md"
    output.write_text("previous")
    def fail(*args):
        raise OSError("simulated replacement failure")
    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(InputError, match="WriteError"):
        atomic_write(output, "new")
    assert output.read_text() == "previous"
    assert list(tmp_path.iterdir()) == [output]


def test_corrupted_expectations_are_not_used(tmp_path):
    directory, state = setup_fixture(tmp_path)
    (directory / "expectations.json").write_text("broken ground truth")
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
    assert json.loads(state.read_text())["counts"]["paths"] == 20


def test_bad_result_named_error(tmp_path, capsys):
    path = tmp_path / "state.json"
    path.write_text("{}")
    assert main(["report", "--state", str(path)]) == 2
    assert "SchemaError" in capsys.readouterr().err


def test_duplicate_json_fields_rejected(tmp_path, capsys):
    (tmp_path / "dataset.json").write_text('{"synthetic": true, "synthetic": false}')
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and "duplicate JSON field" in error and "line 1" in error


def test_corrupted_fixture_changes_cli_report(tmp_path, capsys):
    directory, state = setup_fixture(tmp_path)
    dataset = directory / "dataset.json"
    data = json.loads(dataset.read_text())
    data["records"][0]["known"] = False
    dataset.write_text(json_text(data), encoding="utf-8")
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
    capsys.readouterr()
    assert main(["report", "--format", "json", "--state", str(state)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["counts"]["paths"] == 18
    assert report["counts"]["reachable_targets"] == 9


def test_malformed_result_fields_named_error(tmp_path, capsys):
    directory, state = setup_fixture(tmp_path)
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
    data = json.loads(state.read_text())
    data["paths"] = [None]
    state.write_text(json_text(data), encoding="utf-8")
    assert main(["report", "--state", str(state)]) == 2
    assert "SchemaError" in capsys.readouterr().err


def test_unicode_cli_subprocess(tmp_path):
    from referral_mapper.fixtures import tiny_fixture
    data = tiny_fixture()
    data["records"][0]["name"] = "李 Zoë " + "x" * 9000 + r" C:\Users\henry"
    (tmp_path / "dataset.json").write_text(json_text(data), encoding="utf-8")
    state = tmp_path / "state.json"
    command = [sys.executable, "-m", "referral_mapper.cli"]
    process = subprocess.run(command + ["run", "--input", str(tmp_path), "--state", str(state)], capture_output=True, encoding="utf-8")
    assert process.returncode == 0
    process = subprocess.run(command + ["report", "--state", str(state)], capture_output=True, encoding="utf-8")
    assert process.returncode == 0
    assert data["records"][0]["name"].split()[0] in process.stdout


def test_no_em_dashes_in_project_sources():
    project = Path(__file__).resolve().parents[1]
    files = list((project / "referral_mapper").glob("*.py")) + list((project / "tests").glob("*.py"))
    files += list(project.glob("*.md"))
    for path in files:
        assert chr(0x2014) not in path.read_text(encoding="utf-8")
