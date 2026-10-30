import pytest

from lingo_ledger.workflow import Document, Domain, Status, approve, translate


class FakeTranslator:
    def translate(self, text, source_lang, target_lang, domain):
        return f"[{target_lang}] {text}"


def make_doc(text="Hello"):
    return Document("d1", "en", "es", text, Domain.IMMIGRATION)


def test_translate_sets_draft_and_needs_review():
    doc = translate(make_doc(), FakeTranslator())
    assert doc.translation == "[es] Hello"
    assert doc.status is Status.NEEDS_REVIEW


def test_translate_rejects_empty_text():
    with pytest.raises(ValueError):
        translate(make_doc("   "), FakeTranslator())


def test_approve_requires_human_reviewer():
    doc = translate(make_doc(), FakeTranslator())
    with pytest.raises(ValueError):
        approve(doc, "")
    approve(doc, "reviewer-42")
    assert doc.status is Status.APPROVED
    assert "approved by reviewer-42" in doc.notes


def test_cannot_approve_untranslated_document():
    with pytest.raises(ValueError):
        approve(make_doc(), "reviewer-42")
