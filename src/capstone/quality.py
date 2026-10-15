"""Quality axis — consumes the eval metrics produced by ``domain-llm-finetune``.

The sibling fine-tune repo scores a grounded-or-refuse policy assistant with
deterministic metrics (overall_pass_rate, grounded_citation_rate,
hallucinated_citation_rate, refusal_accuracy, false_refusal_rate,
correct_citation_rate). Here we fold those into one 0..1 composite and a
pass/fail quality gate, so quality can be compared on the same scale as cost,
privacy and complexity.

Pure functions only; no model, no network.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import QUALITY_BAR_PASS_RATE, QUALITY_MAX_HALLUCINATION

# How much each metric contributes to the composite. "Trust" behaviours
# (grounding, refusing correctly, not hallucinating citations) are weighted as
# heavily as raw task success — that is the whole point of a regulated-domain
# assistant.
_METRIC_WEIGHTS = {
    "overall_pass_rate": 0.35,
    "grounded_citation_rate": 0.20,
    "refusal_accuracy": 0.15,
    "correct_citation_rate": 0.10,
    "hallucinated_citation_rate": 0.12,   # lower is better -> inverted below
    "false_refusal_rate": 0.08,           # lower is better -> inverted below
}
_LOWER_IS_BETTER = {"hallucinated_citation_rate", "false_refusal_rate"}


@dataclass
class QualityProfile:
    """One option's quality, in the metric vocabulary of the fine-tune repo."""

    overall_pass_rate: float
    grounded_citation_rate: float
    refusal_accuracy: float
    correct_citation_rate: float
    hallucinated_citation_rate: float
    false_refusal_rate: float

    def as_dict(self) -> dict:
        return {
            "overall_pass_rate": self.overall_pass_rate,
            "grounded_citation_rate": self.grounded_citation_rate,
            "refusal_accuracy": self.refusal_accuracy,
            "correct_citation_rate": self.correct_citation_rate,
            "hallucinated_citation_rate": self.hallucinated_citation_rate,
            "false_refusal_rate": self.false_refusal_rate,
        }


def composite_quality_score(q: QualityProfile) -> float:
    """Blend the metrics into a single 0..1 score (higher is better)."""
    values = q.as_dict()
    score = 0.0
    for metric, weight in _METRIC_WEIGHTS.items():
        v = values[metric]
        contribution = (1.0 - v) if metric in _LOWER_IS_BETTER else v
        score += weight * contribution
    return round(score, 4)


def meets_quality_bar(q: QualityProfile) -> bool:
    """A hard gate: enough task success *and* few hallucinated citations.

    Cost cannot buy its way past this; an option that fails the bar is not a
    candidate regardless of how cheap it is.
    """
    return (
        q.overall_pass_rate >= QUALITY_BAR_PASS_RATE
        and q.hallucinated_citation_rate <= QUALITY_MAX_HALLUCINATION
    )
