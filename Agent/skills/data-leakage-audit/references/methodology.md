# Leakage Methodology

The primary methodology source is Kapoor and Narayanan (2023), DOI
`10.1016/j.patter.2023.100804`. Apply its central data-flow perspective: a
held-out estimate loses independence when information from evaluation data
influences preprocessing, representation, feature selection, hyperparameters,
checkpoint selection, or other model-development choices.

Entity overlap is claim-dependent. Repeated records across splits can transmit
information and constitute leakage; they can also make the test population
easier than the claimed deployment population. Use both mechanism IDs only
when both failure chains are stated separately.

Reporting checklists provide questions about split and preprocessing details,
but they do not establish that an undocumented operation was performed
incorrectly. Preserve this distinction in the status.
