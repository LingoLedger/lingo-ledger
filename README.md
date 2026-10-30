<img src="docs/assets/logo.png" alt="Lingo Ledger" width="161">

# Lingo Ledger

Open-weight translation tooling for legal, immigration, and government documents. Lingo Ledger is built around one rule: a model drafts, and only a certified human reviewer approves.

## About

Lingo Ledger helps organisations find government-certified translators and interpreters across the major accreditation systems: NAATI, CATTI, ATA, ITI, and sworn or accredited registers. A customer submits a project brief, covering either a document that needs official certification (immigration, court, or regulatory use) or an interpreting assignment. Lingo Ledger then checks the brief and matches it to qualified professionals.

Planned capabilities, not yet built: searching public certification registers, drafting outreach to translators, and consolidating responses into a side-by-side comparison. Outreach will only send after the customer approves it. Enterprise security, audit trails, and secure document handling are also planned and aren't in this release.

Audience: migration and visa agencies, language service providers, legal practices, healthcare providers, government departments, multinational companies, and international organisations that need officially recognised translations.

## Interfaces

Lingo Ledger ships three interfaces over the same logic:

| Interface | Use it for | Where |
|---|---|---|
| CLI (`lingo`) | Scripts and terminal use | `src/lingo_ledger/cli.py` |
| MCP server (`lingo-mcp`) | AI agents that call tools over stdio | `src/lingo_ledger/mcp_server.py` |
| TypeScript API | Node and TypeScript apps | `ts/src/index.ts` |

CLI examples:

```bash
lingo brief validate brief.json
lingo eval reference.jsonl hypotheses.txt
```

TypeScript example:

```ts
import { validateBrief, scoreTranslations } from "@lingoledger/lingo-ledger";

const check = validateBrief(JSON.parse(briefText));
if (!check.ok) console.error(check.errors);
```

Both the MCP server and the TypeScript API expose `validate_project_brief` (`validateBrief`) and `score_translations` (`scoreTranslations`). The brief check only validates the input. It never contacts a translator.

## Features

These three features follow the Y Combinator Winter 2027 Requests for Startups that fit this project best.

1. **Own your intelligence (open-weight models).** Fine-tune an open-weight model on permitted certified translation and interpretation work, instead of renting a frontier model. Buyers can run it on their own hardware, including courts and agencies that can't send documents to a third party. *Status: planned. Blocked on permitted training data.*
2. **Vertical legal and government translation model.** Specialize a model for legal, immigration, and government terminology with a small curated dataset and an open evaluation set. *Status: evaluation harness exists; no model yet.*
3. **Government document workflow (AI for City Hall).** Intake of scanned government forms, machine translation, human review by a certified translator, and routing. It's aimed at city agencies, courts, and immigration offices, which go beyond the city-government focus of the RFS. *Status: review workflow stub exists; intake not started.*

Source: [Y Combinator Requests for Startups](https://www.ycombinator.com/rfs).

## Layers

| Layer | Status | Where |
|---|---|---|
| Project brief validation | Done, with tests (Python, TypeScript) | `src/lingo_ledger/brief.py`, `ts/src/index.ts` |
| Document workflow: translate, review, approve | Stub with tests | `src/lingo_ledger/workflow.py` |
| Evaluation harness: exact match and token F1 | Baseline with tests (Python, TypeScript) | `src/lingo_ledger/evaluate.py`, `ts/src/index.ts` |
| CLI, MCP server, TypeScript API | Done, with tests | see Interfaces |
| Domain fine-tuning data and recipe | Not started | `training/` |
| Intake: scanned forms to text | Not started | planned |

## Quick start

Python (CLI and MCP server):

```bash
pip install -e ".[dev]"
pytest
```

TypeScript API (Node 22.6 or later, which runs `.ts` files directly):

```bash
cd ts
npm test
```

Run the MCP server with `lingo-mcp`. It needs the `mcp` extra, which `.[dev]` includes.

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
