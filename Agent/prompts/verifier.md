Verify one proposed manuscript assessment using only the supplied numbered MMD
and the proposed JSON. Do not search externally and do not introduce a new
weakness.

Check:

1. Does every quote occur at the stated lines?
2. Does the supporting evidence establish the stated procedure, rather than
   merely omit a detail?
3. Does the causal chain connect the procedure to the claim consequence?
4. Is relevant counterevidence ignored or misused?
5. Is the status no stronger than the evidence permits?

Return JSON with `verdict` (`accept`, `downgrade`, or `reject`),
`recommended_status`, `reasons`, and `counterevidence_handling`. A verifier
cannot promote a result to `confirmed_flaw`; it may only retain, downgrade, or
reject the proposed status.
