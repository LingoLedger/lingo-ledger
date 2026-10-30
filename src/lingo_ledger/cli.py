"""Command-line interface for Lingo Ledger.

    lingo brief validate brief.json
    lingo eval reference.jsonl hypotheses.txt
    lingo search brief.json [--registry export.jsonl]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lingo_ledger.brief import load_brief, validate_brief
from lingo_ledger.evaluate import load_examples, score
from lingo_ledger.naati_guide import naati_search_steps
from lingo_ledger.registry import load_bundled_sample, load_practitioners, search_practitioners


def _cmd_brief_validate(args: argparse.Namespace) -> int:
    try:
        brief = load_brief(args.file)
    except (OSError, json.JSONDecodeError) as err:
        print(f"error: cannot read brief {args.file}: {err}", file=sys.stderr)
        return 1
    if not isinstance(brief, dict):
        print("error: brief must be a JSON object", file=sys.stderr)
        return 1
    check = validate_brief(brief)
    if check.ok:
        print("brief is valid")
        return 0
    for error in check.errors:
        print(f"error: {error}", file=sys.stderr)
    return 1


def _cmd_eval(args: argparse.Namespace) -> int:
    examples = load_examples(args.reference)
    hypotheses = Path(args.hypotheses).read_text(encoding="utf-8").splitlines()
    print(json.dumps(score(examples, hypotheses), indent=2))
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    try:
        brief = load_brief(args.brief)
    except (OSError, json.JSONDecodeError) as err:
        print(f"error: cannot read brief {args.brief}: {err}", file=sys.stderr)
        return 1
    pool = load_practitioners(args.registry) if args.registry else load_bundled_sample()
    try:
        matches = search_practitioners(brief, pool)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    print(json.dumps(matches, indent=2))
    return 0


def _cmd_naati_steps(args: argparse.Namespace) -> int:
    try:
        brief = load_brief(args.brief)
    except (OSError, json.JSONDecodeError) as err:
        print(f"error: cannot read brief {args.brief}: {err}", file=sys.stderr)
        return 1
    try:
        guide = naati_search_steps(brief)
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    print(f"Search by hand at {guide['url']}:")
    for i, step in enumerate(guide["steps"], 1):
        print(f"{i}. {step}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lingo", description="Lingo Ledger: sourcing government-certified translation and interpreting (NAATI, CATTI, ATA, ITI, global certifications)")
    sub = parser.add_subparsers(dest="command", required=True)

    brief = sub.add_parser("brief", help="work with project briefs")
    brief_sub = brief.add_subparsers(dest="brief_command", required=True)
    validate = brief_sub.add_parser("validate", help="check a brief file")
    validate.add_argument("file")
    validate.set_defaults(func=_cmd_brief_validate)

    search = sub.add_parser("search", help="find certified practitioners for a brief")
    search.add_argument("brief", help="brief JSON file")
    search.add_argument("--registry", help="practitioner JSONL export (default: bundled sample)")
    search.set_defaults(func=_cmd_search)

    naati = sub.add_parser("naati-steps", help="print steps to search the NAATI directory by hand")
    naati.add_argument("brief", help="brief JSON file")
    naati.set_defaults(func=_cmd_naati_steps)

    ev = sub.add_parser("eval", help="score hypotheses against a reference set")
    ev.add_argument("reference", help="JSONL file, one example per line")
    ev.add_argument("hypotheses", help="text file, one translation per line")
    ev.set_defaults(func=_cmd_eval)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
