from capstone.quality import meets_quality_bar
from capstone.scenario import CLOSED, SELFHOST, reference_scenario


def test_reference_scenario_is_well_formed():
    s = reference_scenario()
    assert s.workload.requests_per_month > 0
    assert s.closed_pricing.usd_per_1m_output > 0
    assert s.selfhost_serving.output_tokens_per_s > 0


def test_both_options_clear_the_quality_bar():
    s = reference_scenario()
    assert meets_quality_bar(s.closed.quality) is True
    assert meets_quality_bar(s.selfhost.quality) is True


def test_option_names_are_stable():
    assert CLOSED == "closed_api"
    assert SELFHOST == "selfhost_tuned"
