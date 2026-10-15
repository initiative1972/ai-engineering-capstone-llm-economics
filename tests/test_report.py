from capstone import pipeline, report
from capstone.scenario import reference_scenario


def _sensitivity(scenario):
    from capstone.config import WEIGHT_PROFILES
    return {
        p: pipeline.run(scenario, p).decision.winner.name
        for p in WEIGHT_PROFILES
    }


def test_markdown_has_core_sections():
    scenario = reference_scenario()
    result = pipeline.run(scenario, "regulated_enterprise")
    md = report.render_markdown(result, _sensitivity(scenario))
    assert "## Recommendation" in md
    assert "## Economics (break-even)" in md
    assert "## Four-axis scorecard" in md
    assert "## Sensitivity" in md
    assert "## Honest caveats" in md
    assert "Self-hosted tuned model" in md


def test_markdown_shows_the_flip_in_sensitivity():
    scenario = reference_scenario()
    result = pipeline.run(scenario, "regulated_enterprise")
    md = report.render_markdown(result, _sensitivity(scenario))
    assert "cost_sensitive_startup" in md
    assert "Closed API" in md
