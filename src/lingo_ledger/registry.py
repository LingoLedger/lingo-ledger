"""Certified-practitioner search across registries (NAATI, CATTI, ATA, ITI, sworn, other).

Records come from registry exports or partner feeds, loaded as JSONL. The search
matches a validated project brief against those records. It never contacts a
practitioner.

Each record:
    {"id": "...", "display_name": "...", "scheme": "NAATI",
     "language_pairs": [["en", "es"]], "region": "AU",
     "source_registry": "...", "profile_url": "..."}
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from lingo_ledger.brief import validate_brief

BUNDLED_SAMPLE = Path(__file__).parent / "data" / "practitioners.sample.jsonl"
REQUIRED_RECORD_KEYS = ("id", "display_name", "scheme", "language_pairs", "region", "source_registry")


@dataclass(frozen=True)
class Practitioner:
    id: str
    display_name: str
    scheme: str
    language_pairs: tuple[tuple[str, str], ...]
    region: str
    source_registry: str
    profile_url: str | None = None


def parse_record(record: dict, line_no: int | None = None) -> Practitioner:
    where = f" (line {line_no})" if line_no is not None else ""
    for key in REQUIRED_RECORD_KEYS:
        if key not in record:
            raise ValueError(f"practitioner record{where} missing field: {key}")
    pairs = []
    for pair in record["language_pairs"]:
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) for x in pair):
            raise ValueError(f"practitioner record{where} has a bad language pair: {pair!r}")
        pairs.append((pair[0].lower(), pair[1].lower()))
    return Practitioner(
        id=str(record["id"]),
        display_name=str(record["display_name"]),
        scheme=str(record["scheme"]),
        language_pairs=tuple(pairs),
        region=str(record["region"]),
        source_registry=str(record["source_registry"]),
        profile_url=record.get("profile_url"),
    )


def load_practitioners(path: str | Path) -> list[Practitioner]:
    """Read a JSONL export. Raises ValueError with the line number on bad records."""
    records = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            records.append(parse_record(json.loads(line), line_no))
    return records


def search_practitioners(brief: dict, practitioners: Iterable[Practitioner]) -> list[dict]:
    """Return practitioners whose scheme is accepted by the brief and who work the brief's language pair.

    A pair matches in either direction, since many translators work both ways.
    Results are sorted by display name.
    """
    check = validate_brief(brief)
    if not check.ok:
        raise ValueError("invalid brief: " + "; ".join(check.errors))

    source = brief["source_lang"].lower()
    target = brief["target_lang"].lower()
    accepted = set(brief["certifications"])

    matches = []
    for p in practitioners:
        if p.scheme not in accepted:
            continue
        direction = None
        if (source, target) in p.language_pairs:
            direction = f"{source}->{target}"
        elif (target, source) in p.language_pairs:
            direction = f"{target}->{source}"
        if direction is None:
            continue
        matches.append(
            {
                "id": p.id,
                "display_name": p.display_name,
                "scheme": p.scheme,
                "region": p.region,
                "source_registry": p.source_registry,
                "profile_url": p.profile_url,
                "matched_direction": direction,
            }
        )
    return sorted(matches, key=lambda m: m["display_name"])


def load_bundled_sample() -> list[Practitioner]:
    return load_practitioners(BUNDLED_SAMPLE)
