"""Project briefs: what a customer submits before any translator is contacted.

A brief describes the work (languages, purpose, accepted certifications). Validation
only checks the brief. It never contacts translators or sends messages.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

PURPOSES = {"immigration", "court", "regulatory", "medical", "other"}
CERTIFICATION_SCHEMES = {"NAATI", "CATTI", "ATA", "ITI", "sworn", "other"}
REQUIRED_KEYS = ("title", "source_lang", "target_lang", "purpose", "certifications")


@dataclass
class BriefCheck:
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_brief(brief: dict) -> BriefCheck:
    check = BriefCheck()
    for key in REQUIRED_KEYS:
        if key not in brief:
            check.errors.append(f"missing field: {key}")
    if check.errors:
        return check

    if not str(brief["title"]).strip():
        check.errors.append("title must not be empty")
    for key in ("source_lang", "target_lang"):
        value = str(brief[key])
        if not value.strip():
            check.errors.append(f"{key} must not be empty")
    if brief["source_lang"] == brief["target_lang"]:
        check.errors.append("source_lang and target_lang must differ")
    if brief["purpose"] not in PURPOSES:
        check.errors.append(f"purpose must be one of: {', '.join(sorted(PURPOSES))}")
    certs = brief["certifications"]
    if not isinstance(certs, list) or not certs:
        check.errors.append("certifications must be a non-empty list")
    else:
        unknown = sorted(set(certs) - CERTIFICATION_SCHEMES)
        if unknown:
            check.errors.append(f"unknown certifications: {', '.join(unknown)}")
    return check


def load_brief(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
