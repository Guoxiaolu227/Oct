# Evidence Detector: Next-Step Specification

Status: design only; no implementation exists in v0.1.0.

## Responsibility Boundary

The future Evidence Detector will retrieve traceable manuscript, appendix,
code, dataset, or external evidence. It will not decide whether a weakness is
valid. Skills formulate a claim and evidence need; the detector returns source
material; the verifier judges whether the cited material entails the result.

The current runner instead supplies the complete MMD and validates exact
quotes against it. No retrieval quality claim should be inferred from current
results.

## Proposed Interface

```python
async def search_evidence(
    *,
    review_run_id: str,
    paper_id: str,
    claim: str,
    mechanism_ids: list[str],
    query: str,
    scopes: list[str] | None = None,
    polarity: str = "both",
    top_k: int = 10,
) -> list[Evidence]: ...
```

`polarity` is one of `supporting`, `counterevidence`, or `both`. Each result
must include source identity, immutable content hash, page/section/character
location, exact text, retrieval query, retrieval rank, and backend version.

## Search Trace

Each request will emit `evidence_search_started`, `evidence_candidate_returned`,
and `evidence_search_completed` events sharing the parent Skill span. A search
trace must record requested scopes, actually searched sources, query, backend,
top-k, returned IDs, latency, and failure/coverage status.

## Migration Constraint

The future detector must produce the existing `Evidence` contract. It may not
change `MechanismAssessment` or erase the distinction between supporting
evidence, counterevidence, and missing information. Existing MMD-inline runs
remain reproducible via `evidence_mode: inline_document`.

## Deferred Validation

The next phase must independently evaluate localization recall, quote fidelity,
counterevidence recall, and retrieval cost. Retrieval quality must not be
estimated from the downstream model's self-assessment.
