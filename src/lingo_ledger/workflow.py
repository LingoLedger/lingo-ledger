"""Document workflow: intake -> translate -> human review -> routing.

The translator is a protocol so any model (open-weight or hosted) can be plugged in.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Domain(str, Enum):
    LEGAL = "legal"
    IMMIGRATION = "immigration"
    GOVERNMENT = "government"
    GENERAL = "general"


class Status(str, Enum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"


@dataclass
class Document:
    doc_id: str
    source_lang: str
    target_lang: str
    text: str
    domain: Domain = Domain.GENERAL
    status: Status = Status.DRAFT
    translation: str | None = None
    notes: list[str] = field(default_factory=list)


class Translator(Protocol):
    def translate(self, text: str, source_lang: str, target_lang: str, domain: Domain) -> str: ...


def translate(doc: Document, translator: Translator) -> Document:
    """Fill in a draft translation. Never marks the document approved."""
    if not doc.text.strip():
        raise ValueError(f"{doc.doc_id}: empty source text")
    doc.translation = translator.translate(doc.text, doc.source_lang, doc.target_lang, doc.domain)
    doc.status = Status.NEEDS_REVIEW
    return doc


def approve(doc: Document, reviewer_id: str) -> Document:
    """Only a certified human reviewer approves. The model cannot."""
    if doc.status is not Status.NEEDS_REVIEW:
        raise ValueError(f"{doc.doc_id}: must be in needs_review before approval")
    if not reviewer_id:
        raise ValueError("a reviewer id is required")
    doc.status = Status.APPROVED
    doc.notes.append(f"approved by {reviewer_id}")
    return doc
