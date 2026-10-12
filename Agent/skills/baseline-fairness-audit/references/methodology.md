# Baseline Fairness Methodology

Dodge et al. (2019; DOI `10.18653/v1/D19-1224`) show that final test scores
alone can hide material differences in model-selection and computation budgets.
Henderson et al. (2018; DOI `10.1609/aaai.v32i1.11694`) motivate checking
randomness and implementation sensitivity. Dahl et al. (2023; arXiv
`2306.07179`) motivates benchmark rules that make tuning and workload
conditions interpretable.

The audit is claim-relative. An efficiency claim makes compute central; a
same-data algorithmic comparison makes data and selection symmetry central.
Differences must be observed and causally relevant, not counted as checklist
violations.
