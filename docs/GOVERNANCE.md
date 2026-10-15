# Governance & trust layer

The capstone's privacy axis is backed by a concrete trust model. This is the
regulated-domain moat: not "the model is good", but "we can prove where the data
went, who saw it, and that we can turn it off and reproduce what happened".

## The seven dimensions (and how a self-hosted tuned model scores)

| Dimension | What it means | Self-host (open-weight) | Closed API |
|---|---|---|---|
| **data_residency** | data stays on-prem / in-region | Strong — never leaves the tenancy | Weak — egresses to the vendor |
| **pii_handling** | PII redaction + control | Strong — you own the pipeline | Partial — contractual, not technical |
| **auditability** | who-saw-what, full traces | Strong — span tree per request (`multi-agent-prod`) | Partial — vendor logs only |
| **access_control** | RBAC / least privilege | Strong — tool broker + allow-lists | Partial — API key scope |
| **model_transparency** | known weights / provenance | Strong — open weights, pinned | Weak — opaque, can change under you |
| **low_vendor_lock_in** | portability | Strong — move clouds/GPUs freely | Weak — rewrite to switch |
| **incident_recovery** | roll back / reproduce | Strong — pinned weights + traces | Partial — depends on vendor |

Each is scored 0 (absent) / 1 (partial) / 2 (strong) in `governance.py`, weighted,
and reduced to a 0–1 score. Any dimension scored 0 is raised as a **residual-risk
flag** in the decision record rather than averaged away.

## How this is evidenced, not asserted

- **Auditability / access control** are demonstrated in the sibling
  `multi-agent-prod` repo: every run is a span tree plus a shared-memory
  snapshot, a human-in-the-loop gate records exactly what the human saw, and a
  least-privilege tool broker enforces per-worker allow-lists.
- **Data residency / transparency / lock-in** follow structurally from hosting an
  open-weight model on infrastructure you control (see `llm-serving-bench`).

## PII handling, on-prem option, audit trail (deployment notes)

- **PII** — redact at ingress before any model call; keep the redaction map in a
  controlled store; never log raw PII in traces.
- **On-prem / in-region** — the whole point of the self-host option: weights and
  data stay inside the regulated boundary; no third-party egress.
- **Audit trail** — persist the span tree + decision inputs per request so any
  answer can be reconstructed: what was retrieved, what policy was cited, what
  the human approved.

## Honest limits
This is a *design* scorecard with illustrative scores, not a completed controls
assessment. A production deployment still needs a formal privacy impact
assessment, security review, and red-teaming before go-live.
