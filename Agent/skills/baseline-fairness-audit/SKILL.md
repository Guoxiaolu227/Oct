---
name: baseline-fairness-audit
description: Audit comparative empirical claims for relevant baselines and materially asymmetric data, preprocessing, tuning, compute, pretraining, metric, or selection conditions. Do not require identical architectures or hyperparameters by default.
---

# Baseline Fairness Audit

Determine whether a comparative claim isolates method quality from material
differences in experimental opportunity.

## Protocol

1. Identify the exact superiority, efficiency, robustness, or state-of-the-art
   claim and the comparison needed to test it.
2. Build a comparison table for data, split, preprocessing, tuning protocol,
   search budget, compute, pretraining, metric, run selection, and uncertainty.
3. Mark unknown fields as unknown; do not infer an asymmetry from silence.
4. Explain why each observed difference can alter the specific claim.
5. Seek manuscript evidence that equalizes, justifies, or limits the comparison.

Apply [references/decision-rules.yaml](references/decision-rules.yaml). Read
[references/methodology.md](references/methodology.md) when tuning or compute
budget affects interpretation.

## Invariants

- Different optimal hyperparameters are not themselves unfair.
- Equal parameter counts or architectures are not universal requirements.
- A missing fashionable baseline is not a flaw unless it is necessary for the
  paper's comparative claim.
- Do not infer how an unreported baseline was tuned.
