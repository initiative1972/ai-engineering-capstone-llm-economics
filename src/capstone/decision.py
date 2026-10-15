"""The decision — a weighted, four-axis multi-criteria comparison.

Each option arrives with four already-normalised-ish inputs:

  * quality      0..1  (from quality.composite_quality_score)
  * monthly cost A$    (from economics.evaluate; lower is better)
  * privacy      0..1  (from governance.governance_score)
  * complexity   0..1  (from complexity.operability_score)

Cost is turned into a 0..1 score *relative to the cheapest option on the table*
(cheapest = 1.0). We then apply a named stakeholder weight profile and rank. An
option that fails the hard quality bar is disqualified from winning but still
shown, so the trade-off stays visible and honest.

Pure functions only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .config import AXES, weights_for


@dataclass
class OptionScores:
    """One option's inputs on all four axes."""

    name: str
    quality: float            # 0..1
    monthly_cost_aud: float   # lower is better
    privacy: float            # 0..1
    complexity: float         # 0..1 (operability; higher is better)
    meets_quality_bar: bool = True


@dataclass
class ScoredOption:
    name: str
    axis_scores: Dict[str, float]      # normalised 0..1 per axis
    weighted_total: float
    disqualified: bool
    note: str = ""


@dataclass
class DecisionResult:
    profile: str
    weights: Dict[str, float]
    ranked: List[ScoredOption]
    deciding_axis: str
    rationale: str
    options: List[OptionScores] = field(default_factory=list)

    @property
    def winner(self) -> ScoredOption:
        return self.ranked[0]

    def as_dict(self) -> dict:
        return {
            "profile": self.profile,
            "weights": self.weights,
            "winner": self.winner.name,
            "deciding_axis": self.deciding_axis,
            "rationale": self.rationale,
            "ranked": [
                {
                    "name": o.name,
                    "axis_scores": {k: round(v, 4) for k, v in o.axis_scores.items()},
                    "weighted_total": round(o.weighted_total, 4),
                    "disqualified": o.disqualified,
                    "note": o.note,
                }
                for o in self.ranked
            ],
        }


def _cost_scores(options: List[OptionScores]) -> Dict[str, float]:
    """Relative cost score: cheapest option = 1.0, others scale down."""
    costs = [o.monthly_cost_aud for o in options if o.monthly_cost_aud > 0]
    cheapest = min(costs) if costs else 0.0
    out = {}
    for o in options:
        if o.monthly_cost_aud <= 0 or cheapest <= 0:
            out[o.name] = 1.0
        else:
            out[o.name] = round(cheapest / o.monthly_cost_aud, 4)
    return out


def _deciding_axis(winner: ScoredOption, runner_up: ScoredOption,
                   weights: Dict[str, float]) -> str:
    """The axis contributing the most to the winner's margin over #2."""
    best_axis, best_gap = AXES[0], float("-inf")
    for axis in AXES:
        gap = weights[axis] * (
            winner.axis_scores[axis] - runner_up.axis_scores[axis]
        )
        if gap > best_gap:
            best_gap, best_axis = gap, axis
    return best_axis


def decide(options: List[OptionScores], profile: str) -> DecisionResult:
    """Rank options under a named weight profile."""
    if not options:
        raise ValueError("need at least one option to decide between")
    weights = weights_for(profile)
    cost_scores = _cost_scores(options)

    scored: List[ScoredOption] = []
    for o in options:
        axis_scores = {
            "quality": o.quality,
            "cost": cost_scores[o.name],
            "privacy": o.privacy,
            "complexity": o.complexity,
        }
        total = sum(weights[a] * axis_scores[a] for a in AXES)
        note = "" if o.meets_quality_bar else "below quality bar -> disqualified"
        scored.append(ScoredOption(
            name=o.name,
            axis_scores=axis_scores,
            weighted_total=round(total, 4),
            disqualified=not o.meets_quality_bar,
            note=note,
        ))

    # Eligible options (passing the quality bar) rank ahead of disqualified ones.
    scored.sort(key=lambda s: (not s.disqualified, s.weighted_total), reverse=True)

    if len(scored) >= 2:
        deciding = _deciding_axis(scored[0], scored[1], weights)
        margin = scored[0].weighted_total - scored[1].weighted_total
        rationale = (
            f"{scored[0].name} wins under the '{profile}' profile by "
            f"{margin:.3f}, driven mainly by the {deciding} axis."
        )
    else:
        deciding = max(weights, key=weights.get)
        rationale = f"{scored[0].name} is the only candidate under '{profile}'."

    return DecisionResult(
        profile=profile,
        weights=weights,
        ranked=scored,
        deciding_axis=deciding,
        rationale=rationale,
        options=list(options),
    )
