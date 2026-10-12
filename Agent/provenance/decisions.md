# R3 Agent Decisions

## Frozen Scope

The experiment-facing mechanism IDs remain `FM-R3-01` through `FM-R3-05` to
match `../standards/failure_mechanisms_v0.1.jsonl`. Short labels such as `R3-1`
are display aliases only. The five mechanisms are an initial controlled subset,
not a claim of a mutually exclusive or complete methodology taxonomy.

## Overlap Policy

A weakness may carry multiple mechanism IDs only when the result states a
separate failure path for each. Entity overlap, for example, can support data
leakage when information crosses the evaluation boundary and split bias when
the split unit fails to match the claimed deployment population. Shared text
alone does not justify duplicate labels.

The runner merges cross-Skill findings only when status, normalized claim,
hypothesis, causal chain, supporting/counterevidence IDs, and missing-information
needs are identical. This deliberately conservative rule collapses duplicate
reports while preserving findings with distinct failure chains. `refuted`,
`not_applicable`, and `insufficient_evidence` assessments remain
mechanism-specific.

## Evidence and Missingness

`confirmed_flaw` requires an exact quote from the supplied MMD plus a valid
claim-to-procedure-to-consequence chain. The machine may emit
`reporting_gap/suspected_missing`, but only future human annotation may assign
`verified_missing`. The validator rejects machine-produced verified absence.

## Evidence Detector Boundary

Version 0.1.0 implements only full-MMD loading and exact quote validation. It
does not implement retrieval, PDF parsing, code analysis, dataset inspection,
or external search. Oversized manuscripts fail rather than being truncated.

## Telemetry and Privacy

Every considered and invoked Skill is traceable. Long-lived telemetry contains
IDs, hashes, status, tokens, latency, and assessment references. Manuscript text,
full prompts, and raw responses remain in ignored private run directories.

## Model and Severity

DeepSeek is the default OpenAI-compatible provider, configured only through
environment variables and YAML. Severity and acceptance recommendations are
outside this release and remain `null`.
