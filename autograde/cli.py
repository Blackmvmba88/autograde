from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from autograde import __version__
from autograde.diagnostics import build_diagnostic_report
from autograde.grading import grade_exam
from autograde.rendering import render_exam
from autograde.schema import dump_exam, load_exam, normalize_exam, validate_exam_structure


def cmd_validate(args: argparse.Namespace) -> int:
    exam = load_exam(args.exam)
    errors = validate_exam_structure(exam)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OK")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    exam = load_exam(args.template)
    normalized = normalize_exam(exam)
    errors = validate_exam_structure(normalized)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    dump_exam(normalized, args.out)
    print(args.out)
    return 0


def cmd_grade(args: argparse.Namespace) -> int:
    exam = load_exam(args.exam)
    responses = load_exam(args.responses)
    errors = validate_exam_structure(exam)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    report = grade_exam(exam, responses)
    report["diagnostic"] = build_diagnostic_report(exam, report["results"])
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    exam = load_exam(args.exam)
    errors = validate_exam_structure(exam)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    rendered = render_exam(exam, args.to)
    if args.out:
        Path(args.out).write_text(json.dumps(rendered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(args.out)
    else:
        print(json.dumps(rendered, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autograde")
    parser.add_argument("--version", action="version", version=f"AutoGrade v{__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate an exam JSON file")
    validate_parser.add_argument("exam", type=str)
    validate_parser.set_defaults(func=cmd_validate)

    generate_parser = subparsers.add_parser("generate", help="Copy a template exam to an output file")
    generate_parser.add_argument("--template", required=True, type=str)
    generate_parser.add_argument("--out", required=True, type=str)
    generate_parser.set_defaults(func=cmd_generate)

    grade_parser = subparsers.add_parser("grade", help="Grade a response JSON file against an exam")
    grade_parser.add_argument("--exam", required=True, type=str)
    grade_parser.add_argument("--responses", required=True, type=str)
    grade_parser.set_defaults(func=cmd_grade)

    render_parser = subparsers.add_parser("render", help="Render an exam into a target format")
    render_parser.add_argument("exam", type=str)
    render_parser.add_argument("--to", required=True, type=str, choices=["omr", "web", "pdf", "simulation"])
    render_parser.add_argument("--out", required=False, type=str)
    render_parser.set_defaults(func=cmd_render)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
