from capstone.governance import (
    GovernancePosture,
    governance_flags,
    governance_score,
)


def _selfhost():
    return GovernancePosture(2, 2, 2, 2, 2, 2, 2)


def _closed():
    return GovernancePosture(
        data_residency=0, pii_handling=1, auditability=1, access_control=1,
        model_transparency=0, low_vendor_lock_in=0, incident_recovery=1,
    )


def test_perfect_posture_scores_one():
    assert governance_score(_selfhost()) == 1.0
    assert governance_flags(_selfhost()) == []


def test_closed_posture_lower_and_flagged():
    assert governance_score(_closed()) == 0.28
    assert set(governance_flags(_closed())) == {
        "data_residency", "model_transparency", "low_vendor_lock_in"
    }


def test_score_monotonic_in_a_dimension():
    low = GovernancePosture(0, 0, 0, 0, 0, 0, 0)
    mid = GovernancePosture(1, 1, 1, 1, 1, 1, 1)
    assert governance_score(low) < governance_score(mid) < governance_score(_selfhost())
