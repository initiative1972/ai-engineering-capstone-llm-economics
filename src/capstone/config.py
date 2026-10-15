"""Shared constants: the four decision axes, weight profiles, thresholds, paths.

All values are *illustrative inputs*, not quotes or guarantees. The point of the
repo is that every one of them is explicit and overridable.
"""
from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = BASE_DIR / "reports"

# The four axes of the decision (the JD's four axes).
AXES = ("quality", "cost", "privacy", "complexity")

# Named stakeholder weight profiles. Each must sum to 1.0 across the four axes.
# Different buyers weigh the same evidence differently; the decision is honest
# only if the weights are stated up front.
WEIGHT_PROFILES = {
    "regulated_enterprise": {
        "quality": 0.30, "cost": 0.20, "privacy": 0.40, "complexity": 0.10,
    },
    "balanced": {
        "quality": 0.25, "cost": 0.25, "privacy": 0.25, "complexity": 0.25,
    },
    "cost_sensitive_startup": {
        "quality": 0.20, "cost": 0.45, "privacy": 0.05, "complexity": 0.30,
    },
}

DEFAULT_PROFILE = "regulated_enterprise"

# Quality gate: an option must clear these before it can win on cost alone.
QUALITY_BAR_PASS_RATE = 0.80          # overall_pass_rate floor
QUALITY_MAX_HALLUCINATION = 0.05      # hallucinated_citation_rate ceiling

# Economics defaults.
SECONDS_PER_MONTH = 730 * 3600        # 730 hours (24/7) of capacity
DEFAULT_USD_AUD = 1.52                # illustrative FX; override with a real rate


def weights_for(profile: str) -> dict:
    """Return the weight dict for a named profile (raises on unknown profile)."""
    if profile not in WEIGHT_PROFILES:
        known = ", ".join(sorted(WEIGHT_PROFILES))
        raise KeyError(f"unknown weight profile '{profile}'; known: {known}")
    return dict(WEIGHT_PROFILES[profile])
