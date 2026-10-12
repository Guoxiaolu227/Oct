# R3 Paper Audit Agent

This package audits UTF-8 `.mmd` manuscripts for five frozen R3 mechanisms:
data leakage, sampling/split bias, baseline fairness, metric alignment, and
missing necessary controls. It uses one orchestrator, five independently
versioned skills, deterministic quote validation, a finding verifier, and
append-only invocation telemetry.

The current release intentionally does not implement an Evidence Detector,
PDF parsing, code inspection, external search, severity scoring, or a
naturalistic-paper effectiveness experiment. The full MMD is supplied to the
model. Inputs that exceed the configured character budget fail explicitly.
Reviews also stop before exceeding `execution.max_model_requests_per_run`;
the default hard limit is 15 requests, including retries and verifier calls.

## Setup

```powershell
cd D:\NJUST\WeaknessReviewer\Oct\Agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
$env:DEEPSEEK_API_KEY = "<secret>"
```

All development and review commands below are intended to run from this
project-local virtual environment. `.venv/` is ignored by Git. The key is read
only from the environment and is never written to telemetry.

## Commands

```powershell
python -m r3_agent review paper.mmd --condition progressive --config configs/default.yaml
python -m r3_agent validate result.json
python -m r3_agent summarize-trace runs/private/<review_run_id>
python -m r3_agent export-telemetry runs/private/<review_run_id> --output telemetry.jsonl
python -m r3_agent verify-sources
python -m r3_agent build-manifest
python -m pytest
```

Private manuscripts, complete prompts, and raw model responses are written
under `runs/private/` and ignored by Git. Exported telemetry excludes those
fields and retains artifact hashes, invocation events, token use, latency,
status, and assessment identifiers. A schema-valid sanitized example is in
`examples/sanitized_telemetry.jsonl`.

## Research Boundary

Controlled probes verify engineering invariants only. They are synthetic and
must not be reported as real-paper precision, recall, or evidence that skills
outperform a baseline. A later naturalistic experiment requires independent
human annotation and adjudication.
