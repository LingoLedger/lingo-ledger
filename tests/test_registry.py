import json

import pytest

from lingo_ledger.registry import (
    Practitioner,
    load_bundled_sample,
    load_practitioners,
    parse_record,
    search_practitioners,
)

BRIEF = {
    "title": "Birth certificate for visa",
    "source_lang": "en",
    "target_lang": "es",
    "purpose": "immigration",
    "certifications": ["NAATI", "ITI"],
}


def test_bundled_sample_loads():
    people = load_bundled_sample()
    assert len(people) == 4
    assert all("SAMPLE" in p.display_name for p in people)


def test_search_matches_scheme_and_pair_either_direction():
    matches = search_practitioners(BRIEF, load_bundled_sample())
    assert [m["id"] for m in matches] == ["sample-001", "sample-004"]
    assert matches[0]["matched_direction"] == "en->es"


def test_search_reverse_direction_is_matched():
    brief = {**BRIEF, "source_lang": "es", "target_lang": "en"}
    matches = search_practitioners(brief, load_bundled_sample())
    assert {m["id"] for m in matches} == {"sample-001", "sample-004"}
    assert matches[0]["matched_direction"] == "es->en"


def test_search_excludes_unaccepted_scheme():
    brief = {**BRIEF, "certifications": ["ATA"]}
    assert search_practitioners(brief, load_bundled_sample()) == []


def test_search_rejects_invalid_brief():
    with pytest.raises(ValueError, match="invalid brief"):
        search_practitioners({**BRIEF, "purpose": "tax"}, load_bundled_sample())


def test_parse_record_names_missing_field_and_line():
    with pytest.raises(ValueError, match="line 3.*missing field: scheme"):
        parse_record({"id": "x", "display_name": "x", "language_pairs": [], "region": "AU", "source_registry": "s"}, 3)


def test_parse_record_rejects_bad_pair():
    record = {"id": "x", "display_name": "x", "scheme": "ATA", "language_pairs": [["en"]], "region": "US", "source_registry": "s"}
    with pytest.raises(ValueError, match="bad language pair"):
        parse_record(record)


def test_load_practitioners_from_file(tmp_path):
    p = tmp_path / "export.jsonl"
    p.write_text(json.dumps({"id": "1", "display_name": "A", "scheme": "ATA", "language_pairs": [["EN", "FR"]], "region": "US", "source_registry": "export"}) + "\n")
    people = load_practitioners(p)
    assert people == [Practitioner("1", "A", "ATA", (("en", "fr"),), "US", "export", None)]
