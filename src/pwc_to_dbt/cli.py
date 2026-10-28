"""CLI orchestration and exit statuses; conversion opens no database connection."""
import argparse
import json
from pathlib import Path
import sys

from .dependencies import plan
from .mapping import ConversionError
from .project import compile_models, json_text, write_project
from .source_report import source_report
from .xml_reader import read_xml


def _config(path):
    if path is None:
        return {}

    def no_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ConversionError("error", f"Duplicate configuration key {key!r}")
            result[key] = value
        return result

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Convert supported PowerCenter mapping paths into a local DuckDB dbt project")
    parser.add_argument("xml", type=Path, help="PowerCenter export XML")
    parser.add_argument("--output", "-o", type=Path, help="Absent or empty destination directory")
    parser.add_argument("--bindings", type=Path, help="JSON with exact bindings and original target_relations")
    parser.add_argument("--target", action="append", help="Full target identity; repeat to select several; default: all")
    parser.add_argument("--inventory", action="store_true", help="Print exact target identities without conversion")
    parser.add_argument("--source-report", action="store_true", help="Report whole-export source/connector facts; without --output, generate no SQL")
    args = parser.parse_args(argv)
    try:
        if args.source_report and args.inventory:
            raise ConversionError("error", "--source-report cannot be combined with --inventory")
        if args.source_report and args.output is None and args.target is not None:
            raise ConversionError("error", "--target requires conversion output; source-report scope is whole_export")
        export = read_xml(args.xml)
        if args.inventory:
            print(json_text({"input_sha256": export.sha256, "targets": list(map(str, sorted(export.targets)))}), end="")
            return 0
        if args.source_report and args.output is None:
            print(json_text(source_report(export, _config(args.bindings))), end="")
            return 0
        if args.output is None:
            parser.error("--output is required unless --inventory or --source-report is used")
        if args.output.exists() and (not args.output.is_dir() or any(args.output.iterdir())):
            raise ConversionError("error", f"Destination must be absent or empty: {args.output}")
        configuration = _config(args.bindings)
        planning = plan(export, args.target, configuration)
        artifacts, outcomes = compile_models(planning)
        report = source_report(export, configuration, outcomes=outcomes) if args.source_report else None
        manifest = write_project(args.output, export, planning, artifacts, outcomes, report=report)
        for outcome in manifest["outcomes"]:
            print(f"{outcome['status']}: {outcome['target']}: {outcome['reason']}")
        return 1 if any(outcome.status != "emitted" for outcome in outcomes.values()) else 0
    except (ConversionError, OSError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
