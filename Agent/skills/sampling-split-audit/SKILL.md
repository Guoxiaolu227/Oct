---
name: sampling-split-audit
description: Audit whether data collection, filtering, sampling, and split units support the population, time horizon, site, or entity generalization claimed by an empirical paper. Do not use merely because a random split or narrow dataset exists.
---

# Sampling and Split Audit

Determine whether the sample-generation and partition protocol estimates the
quantity and target population claimed by the manuscript.

## Protocol

1. Extract the target population, distribution, time horizon, site, entity, or
   deployment condition stated or implied by the claim.
2. Extract collection sources, inclusion/exclusion criteria, filters, split
   unit, grouping, and temporal order.
3. Form a specific mismatch hypothesis between the study sample and the target.
4. Seek limitations, subgroup results, scope restrictions, or grouped/temporal
   design that refute or narrow the concern.
5. Return a supported status without imposing universal sampling practices.

Always apply [references/decision-rules.yaml](references/decision-rules.yaml).
Read [references/methodology.md](references/methodology.md) for population and
generalization boundaries.

## Invariants

- Random splitting is not intrinsically biased.
- Stratification and external validation are not universal requirements.
- Documentation frameworks reveal missing context; they are not flaw scores.
- A narrow sample is acceptable when the claim is explicitly equally narrow.
