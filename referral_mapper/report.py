"""Deterministic reports with explicit provenance and unmeasured outcomes."""
import json


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def banner(result):
    if result.get("empty_input"):
        return "Data provenance: NO INPUTS. No real or synthetic records supplied."
    return ("Data provenance: SYNTHETIC fixtures only; no real inputs." if result["synthetic"] else
            "Data provenance: REAL inputs declared Henry's own hand-entered data; declaration is not independently verified. No synthetic fixtures.")


def render(result, format="md"):
    if format == "json":
        return json_text({**result, "provenance_banner": banner(result)})
    if format != "md":
        raise ValueError("ReportError: format must be md or json")
    lines = ["# Referral Mapper", "", banner(result), "", f"As of: {result['as_of']}", "", "Input files: " + json.dumps(result.get("input_files", ["dataset.json"])), "", result["limitations"], "",
             "All counts are computed from supplied inputs. Synthetic results demonstrate computation, not real-world accuracy.", "", "## Computed counts", ""]
    lines += [f"- {key}: {value}" for key, value in sorted(result["counts"].items())]
    lines += ["", "## Possible paths", ""]
    # JSON quoting keeps arbitrary names from becoming Markdown instructions or links.
    for path in result["paths"]:
        lines.append("- " + json.dumps(path, ensure_ascii=False, sort_keys=True))
    if not result["paths"]:
        lines.append("No possible paths in the supplied inputs.")
    lines += ["", "Unreachable target ids: " + json.dumps(result["unreachable_organisation_ids"], ensure_ascii=False), ""]
    return "\n".join(lines)
