from capstone import pipeline
from capstone.scenario import CLOSED, SELFHOST, reference_scenario


def test_pipeline_runs_reference_under_regulated():
    r = pipeline.run(reference_scenario(), "regulated_enterprise")
    assert r.decision.winner.name == SELFHOST
    assert r.economics.cheaper_option == "selfhost"
    assert r.details[CLOSED].governance_flags  # closed has residual risks
    assert not r.details[SELFHOST].governance_flags


def test_pipeline_as_dict_is_serialisable():
    import json
    r = pipeline.run(reference_scenario(), "balanced")
    payload = r.as_dict()
    json.dumps(payload)  # must not raise
    assert payload["decision"]["winner"] == SELFHOST
    assert "economics" in payload


def test_startup_profile_flips_pipeline_winner():
    r = pipeline.run(reference_scenario(), "cost_sensitive_startup")
    assert r.decision.winner.name == CLOSED
