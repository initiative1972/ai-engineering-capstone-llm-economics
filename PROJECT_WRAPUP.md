# Project wrap-up — capstone-llm-economics (interview one-pager)

## The one line
The capstone that ties the portfolio together: it decides whether to self-host a
fine-tuned open-weight model or keep a closed API — on quality, cost, privacy and
complexity — with a break-even TCO model, a governance scorecard, and an honest
sensitivity analysis that flips the answer when the weights change.

## What it demonstrates
- **Economics literacy:** fixed-vs-variable cost, a real break-even volume, ops
  cost included, effective A$/1M tokens — not a single hand-wavy number.
- **A defensible decision, not a pitch:** a weighted four-axis model (MCDA) with
  named stakeholder profiles; the recommendation states *why* it won and *when*
  it flips.
- **Governance as a first-class axis:** seven trust dimensions, residual-risk
  flags, evidenced by the agent repo's traces + HITL + least-privilege broker —
  the regulated-domain moat.
- **Integration:** consumes the three sibling flagships' outputs (`collect.py`),
  rather than re-implementing them.
- **Engineering discipline:** pure-Python core, 38 deterministic tests, green CI
  with no GPU, ADRs for every real decision.

## What's honest about it
- Inputs are synthetic/illustrative; the *engine* runs in CI, the *numbers* come
  from real GPU runs of the siblings.
- The decision is conditional on weights: under a cost-first startup profile the
  closed API wins — I show that rather than hide it.
- Economics ignores one-off migration cost and assumes marginal token cost ≈ 0;
  quality is a heuristic composite; governance is a design scorecard, not an audit.

## 60-second demo
```bash
py -3 -m pytest                         # 38 tests, deterministic
py -3 scripts/run_capstone.py           # writes reports/decision_record.md (+ json + svg)
py -3 scripts/run_capstone.py cost_sensitive_startup   # watch the recommendation flip
```

## The reference result (regulated_enterprise profile)
- Recommendation: **self-host the tuned model**, decided on **privacy**.
- Break-even ≈ **1.10M requests/month**; at 1.5M, self-host saves ~**A$2.7k/mo**
  (A$20 vs A$27 per 1M output tokens).
- Flips to the **closed API** under `cost_sensitive_startup` (by 0.007).

## Where it fits
Flagship #4 of four — the integration/decision layer. #1 fine-tunes
(`domain-llm-finetune`), #2 serves and benchmarks (`llm-serving-bench`), #3 makes
agents operable (`multi-agent-prod`); #4 turns all three into a platform decision
you can defend.

## Likely questions, short answers
- *Isn't self-hosting obviously cheaper?* Only above the break-even volume, and
  only once you count ops — below it, the API wins. I compute the crossover.
- *Why is governance weighted so high?* Under the regulated profile it's the
  deciding axis; under the startup profile it's 5% and the API wins. Both are shown.
- *How do I trust the numbers?* The maths is unit-tested against known values;
  the real inputs come from the sibling repos' GPU runs via `collect.py`.
