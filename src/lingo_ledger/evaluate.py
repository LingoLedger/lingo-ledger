"""Baseline metrics for translation quality.

Standard library only, so the harness runs anywhere. Use sacreBLEU or chrF for
published numbers; these scores are for comparing this project's own models.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Example:
    source: str
    reference: str
    domain: str
    lang_pair: str


def load_examples(path: str | Path) -> list[Example]:
    """Read a JSONL file with keys: source, reference, domain, lang_pair."""
    examples = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        try:
            examples.append(
                Example(row["source"], row["reference"], row["domain"], row["lang_pair"])
            )
        except KeyError as missing:
            raise ValueError(f"{path}:{line_no}: missing key {missing}") from None
    return examples


def token_f1(hypothesis: str, reference: str) -> float:
    hyp = Counter(hypothesis.lower().split())
    ref = Counter(reference.lower().split())
    overlap = sum((hyp & ref).values())
    if overlap == 0:
        return 0.0
    precision = overlap / sum(hyp.values())
    recall = overlap / sum(ref.values())
    return 2 * precision * recall / (precision + recall)


def score(examples: list[Example], hypotheses: list[str]) -> dict[str, float]:
    if len(examples) != len(hypotheses):
        raise ValueError("one hypothesis per example is required")
    if not examples:
        raise ValueError("no examples to score")
    exact = sum(h.strip() == e.reference.strip() for e, h in zip(examples, hypotheses))
    f1 = sum(token_f1(h, e.reference) for e, h in zip(examples, hypotheses))
    return {"exact_match": exact / len(examples), "token_f1": f1 / len(examples)}
