"""MCP server exposing Lingo Ledger tools over stdio.

Run with:  lingo-mcp
Requires the optional dependency:  pip install "lingo-ledger[mcp]"
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from lingo_ledger.brief import validate_brief
from lingo_ledger.evaluate import Example, score

mcp = FastMCP("lingo-ledger")


@mcp.tool()
def validate_project_brief(brief: dict) -> dict:
    """Check a project brief (title, languages, purpose, accepted certifications).

    Only validates the brief. It does not contact any translator.
    """
    check = validate_brief(brief)
    return {"ok": check.ok, "errors": check.errors}


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
