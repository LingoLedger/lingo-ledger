<img src="docs/assets/logo.png" alt="Lingo Ledger" width="161">

# Lingo Ledger

Open-weight translation tooling for legal, immigration, and government documents. Lingo Ledger is built around one rule: a model drafts, and only a certified human reviewer approves.

## Features

These three features follow the Y Combinator Winter 2027 Requests for Startups that fit this project best.

1. **Own your intelligence (open-weight models).** Fine-tune an open-weight model on permitted certified translation and interpretation work, instead of renting a frontier model. Buyers can run it on their own hardware, including courts and agencies that can't send documents to a third party. *Status: planned. Blocked on permitted training data.*
2. **Vertical legal and government translation model.** Specialize a model for legal, immigration, and government terminology with a small curated dataset and an open evaluation set. *Status: evaluation harness exists; no model yet.*
3. **Government document workflow (AI for City Hall).** Intake of scanned government forms, machine translation, human review by a certified translator, and routing. It's aimed at city agencies, courts, and immigration offices, which go beyond the city-government focus of the RFS. *Status: review workflow stub exists; intake not started.*

Source: [Y Combinator Requests for Startups](https://www.ycombinator.com/rfs).

## Layers

| Layer | Status | Where |
|---|---|---|
| Document workflow: translate, review, approve | Stub with tests | `src/lingo_ledger/workflow.py` |
| Evaluation harness: exact match and token F1 | Baseline with tests | `src/lingo_ledger/evaluate.py` |
| Domain fine-tuning data and recipe | Not started | `training/` |
| Intake: scanned forms to text | Not started | planned |

## Quick start

```bash
pip install -e ".[dev]"
pytest
```

## Evaluation

Each example in an evaluation file is one JSON line:

```json
{"source": "...", "reference": "...", "domain": "immigration", "lang_pair": "en-es"}
```

`eval/example.jsonl` shows the format only. Its references are placeholders and are not certified translations, so don't use it for model comparisons.

## Data

Training data must come from sources you have rights to use: public-domain or government-published bilingual texts, or translations contributed under written terms. Do not commit client documents, personal data, or translator personal information. See [`training/README.md`](training/README.md).

## Roadmap

See [`docs/PLAN.md`](docs/PLAN.md). The first milestone is an open-weight model that beats a general baseline on a public legal-translation test set, released with weights, data notes, and an evaluation script.

## License

Apache-2.0. See [LICENSE](LICENSE).
