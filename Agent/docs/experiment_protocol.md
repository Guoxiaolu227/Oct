# Deferred Effectiveness Experiment

The current release does not run a naturalistic-paper experiment. It preserves
four future condition names: `general_review`, `static_r3_checklist`,
`all_skills`, and `progressive`. Only `progressive` is executable in v0.1.0;
the other files are preregistration scaffolds and explicitly carry
`experiment_ready: false`.

Before enabling those conditions, freeze a human annotation protocol, use at
least two independent annotators for the core test set, adjudicate disputes,
and keep the existing test papers inaccessible during prompt and rule changes.
All conditions must share the same manuscript representation, model version,
output contract, and evidence capability. Token, latency, retries, and actual
Skill loads must be reported from telemetry rather than estimated from prompt
length.
