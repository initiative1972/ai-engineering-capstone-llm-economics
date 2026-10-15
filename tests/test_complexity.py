from capstone.complexity import ComplexityProfile, operability_score


def test_managed_closed_is_more_operable_than_selfhost():
    closed = ComplexityProfile(
        managed_ops=2, slo_headroom=2, team_readiness=2,
        small_blast_radius=1, upgrade_simplicity=2,
    )
    selfhost = ComplexityProfile(
        managed_ops=0, slo_headroom=1, team_readiness=1,
        small_blast_radius=1, upgrade_simplicity=1,
    )
    assert operability_score(closed) == 0.925
    assert operability_score(selfhost) == 0.35
    assert operability_score(closed) > operability_score(selfhost)


def test_bounds():
    best = ComplexityProfile(2, 2, 2, 2, 2)
    worst = ComplexityProfile(0, 0, 0, 0, 0)
    assert operability_score(best) == 1.0
    assert operability_score(worst) == 0.0
