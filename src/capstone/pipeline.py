"""Wire the four axes together: scenario -> scores -> economics -> decision.

This is the integration seam of the whole portfolio: quality from the fine-tune
repo, cost from the serving repo, governance/complexity from the agent repo —
combined into one ranked recommendation. Pure functions; fully deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from . import complexity as cx
from . import economics as ec
from . import governance as gov
from . import quality as ql
from .decision import DecisionResult, OptionScores, decide
from .scenario import CLOSED, SELFHOST, Scenario


@dataclass
class OptionDetail:
    name: str
    quality_score: float
    meets_quality_bar: bool
    governance_score: float
    governance_flags: list
    operability_score: float
    monthly_cost_aud: float


@dataclass
class CapstoneResult:
    scenario_name: str
    economics: ec.EconomicsResult
    details: Dict[str, OptionDetail]
    decision: DecisionResult

    def as_dict(self) -> dict:
        return {
            "scenario": self.scenario_name,
            "economics": self.economics.as_dict(),
            "options": {
                name: {
                    "quality_score": d.quality_score,
                    "meets_quality_bar": d.meets_quality_bar,
                    "governance_score": d.governance_score,
                    "governance_flags": d.governance_flags,
                    "operability_score": d.operability_score,
                    "monthly_cost_aud": round(d.monthly_cost_aud, 2),
                }
                for name, d in self.details.items()
            },
            "decision": self.decision.as_dict(),
        }


def run(scenario: Scenario, profile: str) -> CapstoneResult:
    """Run the full capstone decision for one scenario under one weight profile."""
    economics = ec.evaluate(
        scenario.closed_pricing, scenario.selfhost_serving, scenario.workload
    )

    monthly = {
        CLOSED: economics.monthly_cost_closed_aud,
        SELFHOST: economics.monthly_cost_selfhost_aud,
    }

    details: Dict[str, OptionDetail] = {}
    option_scores = []
    for name, opt in ((CLOSED, scenario.closed), (SELFHOST, scenario.selfhost)):
        q_score = ql.composite_quality_score(opt.quality)
        meets = ql.meets_quality_bar(opt.quality)
        g_score = gov.governance_score(opt.governance)
        g_flags = gov.governance_flags(opt.governance)
        op_score = cx.operability_score(opt.complexity)

        details[name] = OptionDetail(
            name=name,
            quality_score=q_score,
            meets_quality_bar=meets,
            governance_score=g_score,
            governance_flags=g_flags,
            operability_score=op_score,
            monthly_cost_aud=monthly[name],
        )
        option_scores.append(OptionScores(
            name=name,
            quality=q_score,
            monthly_cost_aud=monthly[name],
            privacy=g_score,
            complexity=op_score,
            meets_quality_bar=meets,
        ))

    decision = decide(option_scores, profile)
    return CapstoneResult(
        scenario_name=scenario.name,
        economics=economics,
        details=details,
        decision=decision,
    )
