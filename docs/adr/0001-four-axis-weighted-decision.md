# ADR 0001 — A weighted four-axis decision, not a single metric

## Status
Accepted.

## Context
"Should we self-host a fine-tuned open-weight model or keep a closed API?" is
routinely argued on a single axis — usually cost, sometimes a benchmark score.
That produces brittle, contestable decisions: a cost-only view ignores that the
data left the tenancy; a quality-only view ignores that the bill tripled.

The enterprise mandate behind this portfolio names four axes explicitly:
**quality, cost, privacy, complexity**.

## Decision
Score every option on all four axes, normalise each to 0–1 (higher is better),
and combine them with an explicit **stakeholder weight profile** that sums to 1.
Rank by the weighted total. Ship three named profiles (`regulated_enterprise`,
`balanced`, `cost_sensitive_startup`) and make the chosen profile part of the
output.

A hard **quality gate** sits in front of the weighting: an option that fails the
pass-rate / hallucination bar is disqualified from winning regardless of price,
so cost can never buy past a trust failure.

## Consequences
- The recommendation is explicit about *why* it won (the deciding axis) and
  *when it would flip* (the sensitivity table) — defensible in an architecture
  review.
- Weights are a value judgement; surfacing them is honest, hiding them is not.
- Normalisation of the cost axis is *relative to the options on the table*, so
  adding a third option can change cost scores — acceptable and documented.
