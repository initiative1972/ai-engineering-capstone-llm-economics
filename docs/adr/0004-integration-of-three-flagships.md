# ADR 0004 — The capstone integrates the three sibling flagships

## Status
Accepted.

## Context
This is flagship #4 of four. It must not re-implement the other three; it must
*consume* them and add the one thing none of them does alone — a defensible
end-to-end recommendation with the economics and governance attached.

| Flagship | Produces | Feeds the capstone axis |
|---|---|---|
| `domain-llm-finetune` | eval metrics (grounded/citation/refusal) | **quality** |
| `llm-serving-bench` | throughput + A$/1M tokens | **cost** |
| `multi-agent-prod` | trace / HITL / least-privilege posture | **privacy** + **complexity** |

## Decision
Keep the capstone a **pure analysis + decision layer**. The inputs are plain
dataclasses whose shapes mirror the sibling repos' report outputs. `collect.py`
parses those repos' JSON report files into capstone inputs (pure stdlib, so it
is unit-tested in CI against fixtures). The committed demo uses a synthetic
`reference_scenario`; real inputs come from running the siblings on a GPU.

## Consequences
- The honesty line is explicit: the *wiring and maths* run and are tested in CI;
  the *numbers* come from real GPU runs of the siblings (`collect.py` is the
  bridge).
- The capstone has a crisp, non-overlapping job: synthesis and decision.
- Swapping in your own measured numbers is a data change, not a code change.
