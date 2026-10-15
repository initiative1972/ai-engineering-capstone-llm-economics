"""Complexity axis — operability burden (the axis where closed APIs usually win).

Being honest about complexity is what stops this whole exercise from being a
rigged pitch for self-hosting. Running your own GPU inference is genuinely more
operational work than calling an API: you own capacity, upgrades, on-call, and
the blast radius of an outage. This module scores that burden and converts it to
an *operability* score (0..1, higher = easier to run).

Pure functions only.
"""
from __future__ import annotations

from dataclasses import dataclass

# Each factor is scored 0..2 where higher = better operability (less burden).
_FACTOR_WEIGHTS = {
    "managed_ops": 0.30,          # someone else runs the servers
    "slo_headroom": 0.25,         # latency SLO met with room to spare
    "team_readiness": 0.20,       # team already has the skills on hand
    "small_blast_radius": 0.15,   # failure is contained / recoverable
    "upgrade_simplicity": 0.10,   # model/engine upgrades are easy
}
_MAX_PER_FACTOR = 2


@dataclass
class ComplexityProfile:
    """One option's operability factors. Each field is 0, 1 or 2."""

    managed_ops: int
    slo_headroom: int
    team_readiness: int
    small_blast_radius: int
    upgrade_simplicity: int

    def as_dict(self) -> dict:
        return {
            "managed_ops": self.managed_ops,
            "slo_headroom": self.slo_headroom,
            "team_readiness": self.team_readiness,
            "small_blast_radius": self.small_blast_radius,
            "upgrade_simplicity": self.upgrade_simplicity,
        }


def operability_score(c: ComplexityProfile) -> float:
    """Weighted 0..1 operability score (higher = easier/cheaper to run)."""
    values = c.as_dict()
    score = 0.0
    for factor, weight in _FACTOR_WEIGHTS.items():
        score += weight * (values[factor] / _MAX_PER_FACTOR)
    return round(score, 4)
