from capstone.quality import (
    QualityProfile,
    composite_quality_score,
    meets_quality_bar,
)


def _strong():
    return QualityProfile(
        overall_pass_rate=0.91,
        grounded_citation_rate=0.96,
        refusal_accuracy=0.94,
        correct_citation_rate=0.90,
        hallucinated_citation_rate=0.02,
        false_refusal_rate=0.06,
    )


def test_composite_in_unit_range():
    score = composite_quality_score(_strong())
    assert 0.0 <= score <= 1.0
    assert score == 0.9343


def test_lower_is_better_inverted():
    base = _strong()
    worse = QualityProfile(
        overall_pass_rate=base.overall_pass_rate,
        grounded_citation_rate=base.grounded_citation_rate,
        refusal_accuracy=base.refusal_accuracy,
        correct_citation_rate=base.correct_citation_rate,
        hallucinated_citation_rate=0.40,     # much worse
        false_refusal_rate=base.false_refusal_rate,
    )
    assert composite_quality_score(worse) < composite_quality_score(base)


def test_quality_bar_pass_and_fail():
    assert meets_quality_bar(_strong()) is True
    failing = QualityProfile(
        overall_pass_rate=0.70,              # below 0.80 floor
        grounded_citation_rate=0.90,
        refusal_accuracy=0.80,
        correct_citation_rate=0.80,
        hallucinated_citation_rate=0.02,
        false_refusal_rate=0.10,
    )
    assert meets_quality_bar(failing) is False


def test_quality_bar_fails_on_hallucination():
    hallucinating = QualityProfile(
        overall_pass_rate=0.95,
        grounded_citation_rate=0.95,
        refusal_accuracy=0.95,
        correct_citation_rate=0.95,
        hallucinated_citation_rate=0.20,     # above 0.05 ceiling
        false_refusal_rate=0.05,
    )
    assert meets_quality_bar(hallucinating) is False
