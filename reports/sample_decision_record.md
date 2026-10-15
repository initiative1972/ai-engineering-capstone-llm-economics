# Decision record — self-host a tuned open-weight model vs closed API

**Scenario:** Tier-1 bank grounded compliance assistant
**Weight profile:** `regulated_enterprise`

> Synthetic/illustrative inputs. No employer data or systems. Numbers regenerate from `scripts/run_capstone.py`.

## Recommendation

**Self-hosted tuned model.** selfhost_tuned wins under the 'regulated_enterprise' profile by 0.300, driven mainly by the privacy axis.

## Economics (break-even)

- Closed API: **A$10,260/mo** (≈ A$27.36 / 1M output tokens)
- Self-host: **A$7,551/mo** (≈ A$20.14 / 1M output tokens)
- **Break-even:** ~1.10M requests/month — above this, self-hosting is cheaper.
- Cheaper at current volume: **selfhost** (saves A$2,709/mo).
- Self-host capacity: ~23.1M requests/month (within capacity).

## Four-axis scorecard (normalised 0–1, higher is better)

| Axis | Weight | Self-hosted tuned model | Closed API |
|---|---|---|---|
| **quality** | 30% | 0.93 | 0.88 |
| **cost** | 20% | 1.00 | 0.74 |
| **privacy** | 40% | 1.00 | 0.28 |
| **complexity** | 10% | 0.35 | 0.93 |
| **weighted total** |  | **0.915** | **0.615** |

Deciding axis under `regulated_enterprise`: **privacy**.

## Governance flags

- Closed API: residual risks → data_residency, model_transparency, low_vendor_lock_in
- Self-hosted tuned model: residual risks → none

## Sensitivity — who wins under each stakeholder profile

| Weight profile | Winner |
|---|---|
| `regulated_enterprise` | Self-hosted tuned model |
| `balanced` | Self-hosted tuned model |
| `cost_sensitive_startup` | Closed API |

> The recommendation is **not** unconditional: it flips with the weights. Stating the weights is the honest part of the decision.

## Honest caveats

- All inputs are illustrative/synthetic; replace with your own measured quality (fine-tune repo) and throughput (serving repo).
- Economics models fixed-vs-variable cost; it ignores one-off migration effort and assumes reserved-GPU marginal cost ≈ 0.
- Quality is a composite of heuristic metrics, not human eval.
