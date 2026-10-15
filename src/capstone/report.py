"""Render the decision as a one-page Architecture Decision Record (markdown).

Takes the default-profile result plus a sensitivity map (winner per profile) and
produces the human-readable artefact an architecture review board would sign.
Pure string building; deterministic.
"""
from __future__ import annotations

from typing import Dict

from .config import AXES
from .pipeline import CapstoneResult

_NICE = {
    "closed_api": "Closed API",
    "selfhost_tuned": "Self-hosted tuned model",
}


def _nice(name: str) -> str:
    return _NICE.get(name, name)


def _axis_table(result: CapstoneResult) -> str:
    weights = result.decision.weights
    header = "| Axis | Weight | " + " | ".join(
        _nice(o.name) for o in result.decision.ranked
    ) + " |"
    sep = "|" + "---|" * (2 + len(result.decision.ranked))
    rows = [header, sep]
    for axis in AXES:
        cells = [f"**{axis}**", f"{weights[axis]:.0%}"]
        for o in result.decision.ranked:
            cells.append(f"{o.axis_scores[axis]:.2f}")
        rows.append("| " + " | ".join(cells) + " |")
    total_cells = ["**weighted total**", ""]
    for o in result.decision.ranked:
        total_cells.append(f"**{o.weighted_total:.3f}**")
    rows.append("| " + " | ".join(total_cells) + " |")
    return "\n".join(rows)


def render_markdown(result: CapstoneResult, sensitivity: Dict[str, str]) -> str:
    ec = result.economics
    dec = result.decision
    winner = _nice(dec.winner.name)

    lines = []
    lines.append("# Decision record — self-host a tuned open-weight model vs closed API")
    lines.append("")
    lines.append(f"**Scenario:** {result.scenario_name}")
    lines.append(f"**Weight profile:** `{dec.profile}`")
    lines.append("")
    lines.append("> Synthetic/illustrative inputs. No employer data or systems. "
                 "Numbers regenerate from `scripts/run_capstone.py`.")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(f"**{winner}.** {dec.rationale}")
    lines.append("")

    lines.append("## Economics (break-even)")
    lines.append("")
    lines.append(f"- Closed API: **A${ec.monthly_cost_closed_aud:,.0f}/mo** "
                 f"(≈ A${ec.effective_aud_per_1m_tokens_closed:,.2f} / 1M output tokens)")
    eff_self = ec.effective_aud_per_1m_tokens_selfhost
    eff_self_txt = f"A${eff_self:,.2f}" if eff_self is not None else "n/a"
    lines.append(f"- Self-host: **A${ec.monthly_cost_selfhost_aud:,.0f}/mo** "
                 f"(≈ {eff_self_txt} / 1M output tokens)")
    if ec.break_even_requests_per_month is not None:
        lines.append(f"- **Break-even:** ~{ec.break_even_requests_per_month / 1e6:.2f}M "
                     "requests/month — above this, self-hosting is cheaper.")
    lines.append(f"- Cheaper at current volume: **{_nice(ec.cheaper_option)}** "
                 f"(saves A${ec.monthly_saving_aud:,.0f}/mo).")
    cap = ec.selfhost_capacity_requests_per_month
    cap_note = "within capacity" if not ec.over_capacity else "**OVER capacity — add GPUs**"
    lines.append(f"- Self-host capacity: ~{cap / 1e6:.1f}M requests/month ({cap_note}).")
    lines.append("")

    lines.append("## Four-axis scorecard (normalised 0–1, higher is better)")
    lines.append("")
    lines.append(_axis_table(result))
    lines.append("")
    lines.append(f"Deciding axis under `{dec.profile}`: **{dec.deciding_axis}**.")
    lines.append("")

    lines.append("## Governance flags")
    lines.append("")
    for name, d in result.details.items():
        flags = ", ".join(d.governance_flags) if d.governance_flags else "none"
        lines.append(f"- {_nice(name)}: residual risks → {flags}")
    lines.append("")

    lines.append("## Sensitivity — who wins under each stakeholder profile")
    lines.append("")
    lines.append("| Weight profile | Winner |")
    lines.append("|---|---|")
    for profile, win_name in sensitivity.items():
        lines.append(f"| `{profile}` | {_nice(win_name)} |")
    lines.append("")
    lines.append("> The recommendation is **not** unconditional: it flips with the "
                 "weights. Stating the weights is the honest part of the decision.")
    lines.append("")

    lines.append("## Honest caveats")
    lines.append("")
    lines.append("- All inputs are illustrative/synthetic; replace with your own "
                 "measured quality (fine-tune repo) and throughput (serving repo).")
    lines.append("- Economics models fixed-vs-variable cost; it ignores one-off "
                 "migration effort and assumes reserved-GPU marginal cost ≈ 0.")
    lines.append("- Quality is a composite of heuristic metrics, not human eval.")
    lines.append("")
    return "\n".join(lines)
