from capstone.decision import OptionScores, decide


def _options():
    closed = OptionScores(
        name="closed_api", quality=0.8792, monthly_cost_aud=10260.0,
        privacy=0.28, complexity=0.925, meets_quality_bar=True,
    )
    selfhost = OptionScores(
        name="selfhost_tuned", quality=0.9343, monthly_cost_aud=7550.72,
        privacy=1.0, complexity=0.35, meets_quality_bar=True,
    )
    return [closed, selfhost]


def test_regulated_profile_picks_selfhost_on_privacy():
    d = decide(_options(), "regulated_enterprise")
    assert d.winner.name == "selfhost_tuned"
    assert d.deciding_axis == "privacy"


def test_startup_profile_picks_closed():
    d = decide(_options(), "cost_sensitive_startup")
    assert d.winner.name == "closed_api"


def test_balanced_profile_picks_selfhost():
    d = decide(_options(), "balanced")
    assert d.winner.name == "selfhost_tuned"


def test_cheapest_option_gets_full_cost_score():
    d = decide(_options(), "balanced")
    scores = {o.name: o.axis_scores["cost"] for o in d.ranked}
    assert scores["selfhost_tuned"] == 1.0
    assert scores["closed_api"] < 1.0


def test_quality_bar_failure_disqualifies():
    opts = _options()
    opts[1].meets_quality_bar = False       # strongest option fails the bar
    d = decide(opts, "regulated_enterprise")
    assert d.winner.name == "closed_api"
    assert d.ranked[-1].disqualified is True


def test_unknown_profile_raises():
    try:
        decide(_options(), "nope")
        assert False, "expected KeyError"
    except KeyError:
        pass
