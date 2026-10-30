import json

from lingo_ledger.brief import validate_brief
from lingo_ledger.cli import main

GOOD = {
    "title": "Birth certificate for visa",
    "source_lang": "en",
    "target_lang": "es",
    "purpose": "immigration",
    "certifications": ["NAATI"],
}


def test_valid_brief_passes():
    assert validate_brief(GOOD).ok


def test_missing_field_is_reported():
    brief = {k: v for k, v in GOOD.items() if k != "purpose"}
    assert "missing field: purpose" in validate_brief(brief).errors


def test_same_languages_rejected():
    assert not validate_brief({**GOOD, "target_lang": "en"}).ok


def test_unknown_purpose_and_certification_rejected():
    check = validate_brief({**GOOD, "purpose": "tax", "certifications": ["MadeUp"]})
    assert any("purpose" in e for e in check.errors)
    assert any("unknown certifications: MadeUp" in e for e in check.errors)


def test_cli_brief_validate_exit_codes(tmp_path, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(GOOD))
    assert main(["brief", "validate", str(good)]) == 0

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({**GOOD, "purpose": "tax"}))
    assert main(["brief", "validate", str(bad)]) == 1


def test_cli_eval_prints_scores(tmp_path, capsys):
    ref = tmp_path / "ref.jsonl"
    ref.write_text(json.dumps({"source": "s", "reference": "the cat", "domain": "legal", "lang_pair": "en-es"}) + "\n")
    hyp = tmp_path / "hyp.txt"
    hyp.write_text("the cat\n")
    assert main(["eval", str(ref), str(hyp)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["exact_match"] == 1.0


def test_cli_search_prints_matches(tmp_path, capsys):
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps(GOOD))
    assert main(["search", str(brief)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [m["id"] for m in out] == ["sample-001"]


def test_cli_search_rejects_invalid_brief(tmp_path, capsys):
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps({**GOOD, "purpose": "tax"}))
    assert main(["search", str(brief)]) == 1
