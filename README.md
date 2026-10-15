# ai-engineering-capstone-llm-economics
**Should you self-host a fine-tuned open-weight model, or keep paying a closed API?**
A reproducible, governance-aware decision across **quality × cost × privacy × complexity** —
with a break-even total-cost-of-ownership model and the numbers to defend it.

![CI](https://img.shields.io/badge/CI-flake8%20%2B%20pytest-brightgreen)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![tests](https://img.shields.io/badge/tests-38%20passing-brightgreen)
![license](https://img.shields.io/badge/license-MIT-green)

> **Flagship #4 — the capstone.** It ties the portfolio together: #1 fine-tunes the model,
> #2 serves it and measures cost, #3 makes the agent operable — and **this one decides whether
> self-hosting is actually the right call, and proves the economics**. It mirrors the real
> enterprise mandate: *better economics than closed Claude/Gemini/OpenAI, with trust built in.*

---

## The one idea that makes this credible

Most "build vs buy" LLM arguments are made on a single axis (usually cost) and can't survive a
review. This repo makes the decision **four-dimensional, weighted, and honest**:

- a **quality gate** so cheap-but-untrustworthy can never win;
- a **break-even cost model** (fixed self-host vs variable API) with a real crossover volume;
- a **governance scorecard** that treats privacy as a first-class, weighted axis;
- a **sensitivity analysis** that lets the recommendation *flip* when the stakeholder weights
  change — and shows it.

And it's **honest about what runs**:

| Layer | What | Runs where |
|---|---|---|
| **Decision engine** | quality · economics · governance · complexity · decision · report · chart | **CPU, in CI** — pure functions, 38 unit tests |
| **Integration bridge** | `collect.py` parses the sibling repos' JSON reports | **CPU, in CI** — tested against fixtures |
| **Real inputs** | quality (fine-tune repo) + throughput (serving repo) | a **GPU box**, by running the siblings |

The committed demo runs on a synthetic `reference_scenario`, so the whole pipeline — scenario →
scores → economics → decision → report — is deterministic and reproducible with **no GPU, no
network, no secrets**. Inputs are illustrative; swapping in your own measured numbers is a data
change, not a code change.

---

## Quickstart (no GPU required)

```bash
cd capstone-llm-economics
py -3 -m pip install -r requirements-dev.txt

py -3 -m pytest                               # 38 tests, deterministic
py -3 -m flake8 src tests scripts             # clean
py -3 scripts/run_capstone.py                 # -> reports/decision_record.md (+ json + svg)
py -3 scripts/run_capstone.py cost_sensitive_startup   # watch the recommendation flip
```

(`make all` runs lint + tests + demo.)

### What the demo prints

```
scenario            : Tier-1 bank grounded compliance assistant
profile             : regulated_enterprise
recommendation      : selfhost_tuned
deciding axis       : privacy
closed  A$/mo       : 10,260
selfhost A$/mo      : 7,551
break-even req/mo   : 1,103,906
cheaper now         : selfhost (saves A$2,709/mo)
sensitivity         : {'regulated_enterprise': 'selfhost_tuned', 'balanced': 'selfhost_tuned',
                       'cost_sensitive_startup': 'closed_api'}
```

See the full artefact in [`reports/sample_decision_record.md`](reports/sample_decision_record.md).

---

## How the four flagships fit together

```
 #1 domain-llm-finetune ─ quality ─┐
    (grounded / cite / refuse)      │
 #2 llm-serving-bench ──── cost ────┤──►  capstone  ──►  decision record
    (throughput, A$/1M tokens)      │   (this repo)      quality × cost ×
 #3 multi-agent-prod ─ privacy ─────┘    weighted MCDA    privacy × complexity
    (traces, HITL, least privilege)  + complexity          + break-even + governance
```

The capstone **consumes** the siblings' outputs; it does not re-implement them (see
[`docs/adr/0004`](docs/adr/0004-integration-of-three-flagships.md)). `collect.py` is the bridge
that turns their real report JSON into capstone inputs.

---

## The four axes

| Axis | Source | Module | Note |
|---|---|---|---|
| **Quality** | fine-tune eval metrics | `quality.py` | composite + a hard pass/hallucination gate |
| **Cost** | serving throughput + GPU price | `economics.py` | fixed-vs-variable break-even TCO |
| **Privacy** | governance posture | `governance.py` | 7-dimension scorecard + residual-risk flags |
| **Complexity** | operability factors | `complexity.py` | the axis where the closed API usually wins |

The decision (`decision.py`) normalises all four to 0–1, applies a named **weight profile**
(`regulated_enterprise`, `balanced`, `cost_sensitive_startup`), and ranks. An option that fails
the quality gate is disqualified regardless of price.

---

## The economics in one glance

Closed API is variable cost; self-hosting is mostly fixed cost — so there's a **break-even
volume**:

```
closed(v)   = v × per_request_price          # scales forever
selfhost(v) = gpu_reservation + ops          # paid regardless of volume
break_even  = fixed / per_request_price
```

In the reference scenario that crossover is ≈ **1.10M requests/month**; above it, self-hosting
wins. The report also shows the **effective A$/1M output tokens at your volume** (the unit the
serving repo speaks in) and the **capacity** of the reserved GPUs. See
[`docs/adr/0002`](docs/adr/0002-break-even-tco-model.md). A dependency-free SVG of the crossover
is written to `reports/breakeven.svg`.

---

## Why the answer is trustworthy (and not rigged)

- The **closed API genuinely wins the complexity axis** (0.93 vs 0.35) — self-hosting is more
  operational work, and the model says so.
- Under a **cost-first startup profile the closed API wins overall** (by 0.007). The
  recommendation is conditional on the weights, and the sensitivity table shows the flip.
- Governance is the regulated-domain moat, evidenced not asserted — auditability and access
  control come straight from the agent repo's traces, HITL gate, and least-privilege broker. See
  [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md).

---

## Project layout

```
capstone-llm-economics/
├── src/capstone/
│   ├── config.py        # the four axes, weight profiles, thresholds
│   ├── quality.py       # composite quality score + hard quality gate
│   ├── economics.py     # fixed-vs-variable break-even TCO engine
│   ├── governance.py    # 7-dimension trust scorecard + flags
│   ├── complexity.py    # operability score (closed API's winning axis)
│   ├── decision.py      # weighted four-axis MCDA + ranking
│   ├── scenario.py      # the committed synthetic reference scenario
│   ├── pipeline.py      # wires scenario -> scores -> economics -> decision
│   ├── collect.py       # bridge: parse sibling repos' report JSON (tested)
│   ├── report.py        # the decision-record markdown renderer
│   └── chart.py         # dependency-free SVG break-even chart
├── scripts/run_capstone.py
├── tests/               # 38 unit tests (CPU, deterministic)
├── docs/                # 4 ADRs + GOVERNANCE.md
├── reports/sample_decision_record.md
└── .github/workflows/ci.yml   # flake8 + pytest + demo
```

## Testing & CI

GitHub Actions (Python 3.11) runs **flake8 + pytest + the demo** on every push — all on CPU, no
GPU, no secrets. Known values pin the maths (e.g. break-even = 1,103,906; composite quality =
0.9343), so a green badge means the decision logic is correct.

## Honest limitations

- Inputs are **synthetic/illustrative**; replace with your measured quality (fine-tune repo) and
  throughput (serving repo) via `collect.py`.
- The cost model is **fixed-vs-variable**: it ignores one-off migration/build effort and assumes
  reserved-GPU marginal token cost ≈ 0. Both are stated in the report and are easy to extend.
- Quality is a **heuristic composite**, not human eval; governance is a **design scorecard**, not
  a completed controls audit (a production deployment still needs a PIA, security review, and
  red-teaming).

---

*Part of an accelerated AI-engineering portfolio. Author: Henry Yan · github.com/initiative1972.
Synthetic/public data only — no employer data is used or reproduced. MIT © 2026 Henry Yan.*
