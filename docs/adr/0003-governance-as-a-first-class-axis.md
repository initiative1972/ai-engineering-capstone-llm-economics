# ADR 0003 — Governance is a first-class axis, not a footnote

## Status
Accepted.

## Context
Most build-vs-buy LLM analyses treat privacy and governance as a yes/no
afterthought. In a regulated domain (banking, health) it is frequently the
*deciding* factor: where the data resides, whether PII is controlled, whether
every answer is auditable, and whether you are locked to one vendor can outweigh
a cost or quality delta.

## Decision
Score governance as a weighted 0–1 posture across seven dimensions —
`data_residency`, `pii_handling`, `auditability`, `access_control`,
`model_transparency`, `low_vendor_lock_in`, `incident_recovery` — and give it a
real weight in the decision (40% under `regulated_enterprise`). Any dimension
scored 0 is surfaced as a hard **residual-risk flag**, not silently averaged
away.

The auditability and access-control dimensions map directly to the trace +
human-in-the-loop + least-privilege-broker posture demonstrated in the sibling
`multi-agent-prod` repo — i.e. governance here is evidenced, not asserted.

## Consequences
- The regulated-domain advantage of a self-hosted open-weight model (data stays
  in-tenancy, open weights, full traces) becomes a *scored, weighted* input.
- The analysis stays honest: a closed API's residual risks (data egress, opaque
  weights, vendor lock-in) are flagged rather than ignored, and under a
  cost-first profile self-hosting can still lose.
