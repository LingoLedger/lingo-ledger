"""MCP server exposing Lingo Ledger tools over stdio.

Run with:  lingo-mcp
Requires the optional dependency:  pip install "lingo-ledger[mcp]"
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from lingo_ledger.brief import validate_brief
from lingo_ledger.evaluate import Example, score
from lingo_ledger.registry import load_bundled_sample, search_practitioners

mcp = FastMCP(
    "lingo-ledger",
    instructions=(
        "MCP AI Agent for sourcing Gov-Certified Translation & Interpreting Across NAATI, CATTI, ATA, ITI & Global certifications. "
        "Tools: validate_project_brief checks a project brief; search_certified_translators finds "
        "certified practitioners for a brief; score_translations scores translations. "
        "Outreach to practitioners is not yet available."
    ),
)


@mcp.tool()
def validate_project_brief(brief: dict) -> dict:
    """Check a project brief (title, languages, purpose, accepted certifications).

    Only validates the brief. It does not contact any translator.
    """
    check = validate_brief(brief)
    return {"ok": check.ok, "errors": check.errors}


@mcp.tool()
def search_certified_translators(brief: dict, practitioners: list[dict] | None = None) -> dict:
    """Find certified practitioners who match a project brief.

    Matches the brief's language pair (either direction) and accepted certification
    schemes (NAATI, CATTI, ATA, ITI, sworn, other). Pass practitioner records from a
    registry export, or omit them to search the bundled sample data.
    Only searches. It does not contact anyone.
    """
    from lingo_ledger.registry import parse_record

    if practitioners is None:
        pool = load_bundled_sample()
    else:
        pool = [parse_record(r) for r in practitioners]
    return {"matches": search_practitioners(brief, pool)}


@mcp.tool()
def score_translations(examples: list[dict], hypotheses: list[str]) -> dict:
    """Score translations against references.

    Each example needs: source, reference, domain, lang_pair.
    Returns exact_match and token_f1 averages.
    """
    parsed = [
        Example(e["source"], e["reference"], e["domain"], e["lang_pair"]) for e in examples
    ]
    return score(parsed, hypotheses)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
