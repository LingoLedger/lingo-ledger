import pytest

pytest.importorskip("mcp")

from lingo_ledger.mcp_server import score_translations, validate_project_brief  # noqa: E402

GOOD = {
    "title": "Birth certificate for visa",
    "source_lang": "en",
    "target_lang": "es",
    "purpose": "immigration",
    "certifications": ["NAATI"],
}


def test_validate_tool_reports_ok():
    assert validate_project_brief(GOOD) == {"ok": True, "errors": []}


def test_validate_tool_reports_errors():
    result = validate_project_brief({**GOOD, "purpose": "tax"})
    assert result["ok"] is False
    assert any("purpose" in e for e in result["errors"])


def test_score_tool_matches_library():
    examples = [{"source": "s", "reference": "the cat", "domain": "legal", "lang_pair": "en-es"}]
    assert score_translations(examples, ["the cat"])["exact_match"] == 1.0


def test_search_tool_uses_bundled_sample():
    from lingo_ledger.mcp_server import search_certified_translators

    result = search_certified_translators(GOOD)
    assert [m["id"] for m in result["matches"]] == ["sample-001"]


def test_search_tool_accepts_registry_records():
    from lingo_ledger.mcp_server import search_certified_translators

    record = {"id": "r1", "display_name": "Real Export Row", "scheme": "NAATI", "language_pairs": [["en", "es"]], "region": "AU", "source_registry": "export"}
    result = search_certified_translators(GOOD, [record])
    assert [m["id"] for m in result["matches"]] == ["r1"]
