---
name: data-leakage-audit
description: Audit empirical ML manuscripts for evaluation information entering training, preprocessing, feature selection, model selection, or held-out testing. Use when the paper has learned data operations or held-out evaluation; do not use for sampling representativeness alone.
---

# Data Leakage Audit

Determine whether evaluation information improperly influences model
development or the reported generalization estimate.

## Protocol

1. Reconstruct the split, preprocessing, feature-selection, tuning, checkpoint,
   and final-evaluation order from exact manuscript text.
2. State a concrete information-flow hypothesis; do not treat missing detail as
   observed leakage.
3. Check evaluation reuse, fitted preprocessing scope, label-derived inputs,
   and entity or near-duplicate overlap when relevant to the claim.
4. Search the supplied MMD for counterevidence such as an independent
   validation set, grouped split, or frozen final evaluation.
5. Return schema-conforming assessments and abstain when the MMD cannot settle
   actual data flow.

Use [references/decision-rules.yaml](references/decision-rules.yaml) for every
case. Read [references/methodology.md](references/methodology.md) when the
leakage boundary or an overlap with sampling bias is unclear.

## Invariants

- `confirmed_flaw` requires direct evidence that evaluation information crossed
  a development boundary.
- Do not claim that unseen code, data, or duplicates were inspected.
- Missing split order is at most `reporting_gap/suspected_missing`.
- Add `FM-R3-02` only when the same evidence supports a distinct mismatch
  between the split unit and the claimed target population.
