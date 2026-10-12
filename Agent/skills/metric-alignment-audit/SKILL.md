---
name: metric-alignment-audit
description: Audit whether reported metrics, thresholds, aggregation, and subgroup scope measure the capability or consequence claimed by an empirical paper. Do not prescribe a universal metric bundle from the task name alone.
---

# Metric Alignment Audit

Determine whether the evaluation measure supports the paper's stated target
claim under the relevant population and decision conditions.

## Protocol

1. Extract the target task, application consequence, and exact improvement
   claim.
2. Extract each metric's definition, aggregation, threshold, dataset, subgroup,
   and direction of optimization.
3. State what behavior the metric rewards and what claim-relevant errors it can
   hide.
4. Seek complementary metrics, calibration analysis, subgroup results, or
   scope limitations that resolve the concern.
5. Report only a claim-metric mismatch supported by the manuscript.

Apply [references/decision-rules.yaml](references/decision-rules.yaml). Read
[references/methodology.md](references/methodology.md) for measure behavior and
aggregation boundaries.

## Invariants

- Do not require accuracy, precision, recall, and F1 as a universal bundle.
- Class imbalance is relevant only through the target errors and aggregation.
- A proxy metric is acceptable when its relation to the target is established
  or the claim is explicitly limited to the proxy.
