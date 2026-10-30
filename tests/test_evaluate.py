import json

import pytest

from lingo_ledger.evaluate import Example, load_examples, score, token_f1


def test_token_f1_identical_and_disjoint():
    assert token_f1("a b c", "a b c") == 1.0
    assert token_f1("x y", "a b") == 0.0


def test_score_exact_and_partial():
    ex = [Example("s1", "the cat sat", "legal", "en-es"), Example("s2", "go home", "legal", "en-es")]
    result = score(ex, ["the cat sat", "go away"])
    assert result["exact_match"] == 0.5
    assert 0.0 < result["token_f1"] < 1.0


def test_score_rejects_mismatched_lengths():
    ex = [Example("s", "r", "legal", "en-es")]
    with pytest.raises(ValueError):
        score(ex, [])


def test_load_examples_reads_jsonl(tmp_path):
    p = tmp_path / "set.jsonl"
    p.write_text(json.dumps({"source": "s", "reference": "r", "domain": "legal", "lang_pair": "en-es"}) + "\n")
    assert load_examples(p) == [Example("s", "r", "legal", "en-es")]


def test_load_examples_names_missing_key(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps({"source": "s"}) + "\n")
    with pytest.raises(ValueError, match=r":1: missing key"):
        load_examples(p)
