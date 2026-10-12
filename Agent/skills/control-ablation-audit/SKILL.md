---
name: control-ablation-audit
description: Audit whether an empirical paper's component, mechanism, robustness, or causal attribution claims have the necessary contrastive controls. Do not request ablations for system-level effectiveness claims that make no component attribution.
---

# Control and Ablation Audit

Determine whether the experiments distinguish the paper's stated explanation
from plausible alternatives.

## Protocol

1. Identify the exact component, mechanism, robustness, or causal attribution
   claim; if none exists, consider `not_applicable`.
2. List plausible alternative explanations grounded in observed simultaneous
   changes in data, compute, architecture, training, or evaluation.
3. Map the claim to the smallest contrast that would distinguish those
   explanations.
4. Inspect existing ablations, controls, sensitivity analyses, and scope
   limitations for counterevidence.
5. Explain why the missing contrast is necessary, not merely interesting.

Apply [references/decision-rules.yaml](references/decision-rules.yaml). Read
[references/methodology.md](references/methodology.md) for attribution and
ablation boundaries.

## Invariants

- Not every empirical, dataset, or system paper requires a conventional
  ablation.
- Multiple changed components support an overall-system claim but not an
  isolated component attribution.
- A requested extra experiment must change the validity of a stated claim.
