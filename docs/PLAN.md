# Plan

Three layers, one buyer first.

## 1. Base model (Own Your Intelligence)

Start from an open-weight multilingual model. Fine-tune it on permitted translation pairs. Ship the weights and training recipe so buyers can run the model on their own hardware.

## 2. Domain specialization (Vertical Foundation Models)

Specialize for legal, immigration, and government terminology with a small curated set. The open evaluation set is the main contribution at this layer.

## 3. Document workflow (AI for City Hall)

Intake of scanned forms, translation, human review, and routing to a certified translator. Start with immigration documents as the first buyer. Courts and city agencies come after.

## Milestones

1. Workflow and evaluation harness (this repo, done as scaffold).
2. Public legal-translation evaluation set with documented provenance.
3. Baseline scores for a general open-weight model on that set.
4. Fine-tuned model beating the baseline, released with weights, data notes, and eval script.
5. Intake pipeline for scanned forms.

## Open questions

- Which permitted data sources cover immigration terminology?
- Who is the first buyer, and what review standard do they require?
