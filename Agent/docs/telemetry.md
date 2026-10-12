# Skill Invocation Telemetry

Each review is one trace. The review span owns five fixed Skill spans, and each
model request is recorded within the active Skill span. Event ordering is
recoverable from the monotonic `sequence` field even when timestamps collide.

## Research Questions Supported

The event contract permits later measurement of:

- how often each Skill was considered, invoked, completed, or failed;
- which Skill resources and versions were loaded;
- input/output/cached tokens and end-to-end latency per Skill;
- assessment status and finding counts per mechanism;
- retries, parse failures, deterministic rejection, and verifier downgrade;
- cost-quality comparisons after human labels are added.

## Privacy Boundary

`events.jsonl` contains IDs, hashes, counters, resource names, and status. It
does not contain the manuscript, complete prompts, quotes, or model responses.
Those artifacts remain under the ignored private run directory. The export
command further allowlists event-detail keys before producing a research file.

## Incomplete Runs

Events are flushed and fsynced after each append. A trace lacking
`review_completed` is summarized as `incomplete`, including traces ending in
`review_failed`. Statistical analysis must filter or separately report these
runs rather than treating them as zero-finding successes.
