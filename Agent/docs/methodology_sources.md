# R3 Methodology Source Note

## Source Roles

The source registry separates three roles that cannot substitute for one
another:

- Venue guidelines identify what reviewers are expected to examine.
- Scientific methodology explains how a design failure can invalidate an
  estimate, comparison, measurement, or attribution.
- Reporting standards identify information that should be disclosed. Missing
  disclosure is not evidence that the underlying procedure was incorrect.

Every executable decision rule has a stable `rule_id` and at least one edge
in `provenance/traceability_edges.jsonl`. An edge marked `contextual` cannot
independently support a `confirmed_flaw`. An unverified locator is retained as
an explicit research debt rather than presented as a checked quotation.

## Mechanism Mapping

### FM-R3-01: Data leakage

Kapoor and Narayanan's leakage taxonomy motivates reconstructing the data flow
across splitting, preprocessing, feature selection, model selection, and final
evaluation. The audit must distinguish observed evaluation influence from an
undocumented protocol.

### FM-R3-02: Sampling and split bias

Datasheets and Data Statements motivate explicit documentation of collection,
composition, population, and intended use. They support questions about sample
generation and claim scope, but do not by themselves prove bias. A split is
judged relative to the intended unit and horizon of generalization.

### FM-R3-03: Baseline fairness

Show Your Work and related benchmarking work show that test scores depend on
model-selection and computation budgets. Fairness is therefore claim-relative:
different architectures or hyperparameters are not automatically unfair, but
asymmetric data, selection, tuning, or reporting can confound a superiority or
efficiency claim.

### FM-R3-04: Metric alignment

Metric taxonomies and performance-evaluation research motivate mapping the
claimed capability to the metric's mathematical behavior, aggregation,
threshold, and evaluated population. No fixed bundle of metrics is mandatory
for every task.

### FM-R3-05: Necessary controls

Venue claim-evidence criteria, ablation methodology, and causal-design
principles motivate identifying the exact attribution claim and plausible
alternative explanations before requesting a control. A system-level result
does not automatically require component attribution.

## Cross-Cutting Epistemic Rules

All mechanisms apply the same guardrails:

1. Bind each assessment to an explicit manuscript claim or procedure.
2. Require exact manuscript evidence for `confirmed_flaw`.
3. Search the supplied MMD for counterevidence before confirmation.
4. Represent absent reporting as `suspected_missing`; only human review may
   promote it to `verified_missing`.
5. Preserve `refuted`, `not_applicable`, and `insufficient_evidence` outcomes
   instead of manufacturing a criticism.
