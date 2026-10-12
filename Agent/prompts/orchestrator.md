Audit only the active mechanism described below. Follow its SKILL.md and the
loaded decision rules. Return zero or more distinct assessments; do not create
an issue merely to make the list non-empty.

Each assessment must contain:

- `mechanism_ids`: one or more formal `FM-R3-*` IDs.
- `status`: one allowed status.
- `claim_under_review`, `hypothesis`, and a non-empty `causal_chain` unless the
  mechanism is not applicable.
- `supporting_evidence` and `counterevidence`, each containing exact `quote`,
  `start_line`, `end_line`, and `role` values.
- `missing_information`, `missingness_status`, and `resolution_needed`.
- `severity`: always null.

Allowed statuses are `confirmed_flaw`, `plausible_risk`, `reporting_gap`,
`refuted`, `not_applicable`, and `insufficient_evidence`. The machine may use
only `not_missing` or `suspected_missing`; never emit `verified_missing`.

If the mechanism is applicable but no distinct weakness is supported, return
a single `refuted` or `insufficient_evidence` assessment that records what was
checked. If it is not applicable, return one `not_applicable` assessment.
