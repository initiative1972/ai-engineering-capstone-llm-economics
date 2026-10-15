"""The bridge to the sibling flagships: turn their real report files into inputs.

In this repo the demo uses the synthetic ``reference_scenario``. In real life you
would run the sibling repos on a GPU and feed their *actual* report JSON in here:

  * ``domain-llm-finetune`` -> reports/eval_report.json  (quality metrics)
  * ``llm-serving-bench``    -> reports/bench.json         (throughput + cost)

These parsers are pure (stdlib JSON only), so they are unit-tested in CI against
fixtures and never require a GPU. That is the "runs vs design" line for the
integration: the *wiring* is tested here; the *numbers* come from real runs.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .economics import SelfHostServing
from .quality import QualityProfile


def quality_from_metrics(metrics: Dict) -> QualityProfile:
    """Build a QualityProfile from a domain-llm-finetune metrics dict.

    Accepts the aggregate shape emitted by that repo's ``metrics.aggregate``.
    Missing keys default to 0.0 so a partial report still parses.
    """
    def g(key: str) -> float:
        value = metrics.get(key)
        return float(value) if value is not None else 0.0

    return QualityProfile(
        overall_pass_rate=g("overall_pass_rate"),
        grounded_citation_rate=g("grounded_citation_rate"),
        refusal_accuracy=g("refusal_accuracy"),
        correct_citation_rate=g("correct_citation_rate"),
        hallucinated_citation_rate=g("hallucinated_citation_rate"),
        false_refusal_rate=g("false_refusal_rate"),
    )


def quality_from_finetune_report(path: str, which: str = "tuned") -> QualityProfile:
    """Load reports/eval_report.json and pull the 'base' or 'tuned' block."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    block = data.get(which, data)
    return quality_from_metrics(block)


def serving_from_bench(bench: Dict) -> SelfHostServing:
    """Build a SelfHostServing from a llm-serving-bench result dict.

    Expects at least ``output_tokens_per_s``; GPU name/price/ops are optional
    and fall back to sensible, clearly-illustrative defaults.
    """
    return SelfHostServing(
        gpu=str(bench.get("gpu", "A100-80GB")),
        gpu_count=int(bench.get("gpu_count", 1)),
        gpu_usd_per_hr=float(bench.get("gpu_usd_per_hr", 3.20)),
        output_tokens_per_s=float(bench.get("output_tokens_per_s", 0.0)),
        ops_aud_per_month=float(bench.get("ops_aud_per_month", 0.0)),
        reserved_hours_per_month=float(bench.get("reserved_hours_per_month", 730.0)),
    )


def serving_from_bench_report(path: str) -> SelfHostServing:
    """Load a llm-serving-bench JSON report and build a serving config."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return serving_from_bench(data)
