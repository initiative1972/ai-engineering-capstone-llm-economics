"""Privacy / governance axis — the regulated-domain trust scorecard.

In a regulated business the deciding question is often not "which model scores
higher?" but "can we prove where the data went, who saw it, and that we can
turn it off?". This module scores each option across seven trust dimensions and
folds them into one 0..1 governance score, plus a list of hard flags.

The dimensions map to the governance write-up (docs/GOVERNANCE.md) and to the
trace/HITL posture demonstrated in the sibling ``multi-agent-prod`` repo.

Pure functions only.
"""
from __future__ import annotations

from dataclasses import dataclass

# Each dimension is scored 0..2 (0 = absent, 1 = partial, 2 = strong). Weights
# sum to 1.0. "vendor_lock_in" is phrased so that higher = better (i.e. low
# lock-in), to keep every dimension "higher is better".
_DIMENSION_WEIGHTS = {
    "data_residency": 0.22,       # keep data on-prem / in-region
    "pii_handling": 0.18,         # redaction + control over PII
    "auditability": 0.18,         # full trace coverage, who-saw-what
    "access_control": 0.14,       # RBAC / least privilege
    "model_transparency": 0.12,   # open weights, known provenance
    "low_vendor_lock_in": 0.10,   # portability, no single-vendor dependency
    "incident_recovery": 0.06,    # ability to roll back / reproduce
}
_MAX_PER_DIMENSION = 2


@dataclass
class GovernancePosture:
    """One option's trust posture. Each field is 0, 1 or 2."""

    data_residency: int
    pii_handling: int
    auditability: int
    access_control: int
    model_transparency: int
    low_vendor_lock_in: int
    incident_recovery: int

    def as_dict(self) -> dict:
        return {
            "data_residency": self.data_residency,
            "pii_handling": self.pii_handling,
            "auditability": self.auditability,
            "access_control": self.access_control,
            "model_transparency": self.model_transparency,
            "low_vendor_lock_in": self.low_vendor_lock_in,
            "incident_recovery": self.incident_recovery,
        }


def governance_score(p: GovernancePosture) -> float:
    """Weighted 0..1 governance score (higher is better)."""
    values = p.as_dict()
    score = 0.0
    for dim, weight in _DIMENSION_WEIGHTS.items():
        score += weight * (values[dim] / _MAX_PER_DIMENSION)
    return round(score, 4)


def governance_flags(p: GovernancePosture) -> list:
    """Hard flags: dimensions scored 0 are called out as a residual risk."""
    flags = []
    for dim, value in p.as_dict().items():
        if value == 0:
            flags.append(dim)
    return flags
