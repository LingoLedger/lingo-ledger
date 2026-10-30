import json

import pytest

from lingo_ledger.cli import main
from lingo_ledger.naati_guide import DIRECTORY_URL, naati_search_steps

BRIEF = {
    "title": "Birth certificate for visa",
    "source_lang": "en",
    "target_lang": "es",
    "purpose": "immigration",
    "certifications": ["NAATI"],
}


def test_steps_name_the_directory_and_fields():
    guide = naati_search_steps(BRIEF)
    assert guide["url"] == DIRECTORY_URL
    text = " ".join(guide["steps"])
    assert "translate from en and translate into es" in text
    assert "Certified" in text
    assert "Immigration" in text


def test_domain_is_omitted_when_brief_has_none():
    guide = naati_search_steps({**BRIEF, "purpose": "other"})
    assert not any("Under Domain" in s for s in guide["steps"])


def test_rejects_brief_without_naati():
    with pytest.raises(ValueError, match="does not accept NAATI"):
        naati_search_steps({**BRIEF, "certifications": ["ATA"]})


def test_rejects_invalid_brief():
    with pytest.raises(ValueError, match="invalid brief"):
        naati_search_steps({**BRIEF, "purpose": "tax"})


def test_cli_prints_numbered_steps(tmp_path, capsys):
    brief = tmp_path / "brief.json"
    brief.write_text(json.dumps(BRIEF))
    assert main(["naati-steps", str(brief)]) == 0
    out = capsys.readouterr().out
    assert DIRECTORY_URL in out
    assert "1. Open" in out
