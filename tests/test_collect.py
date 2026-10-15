import json

from capstone.collect import (
    quality_from_finetune_report,
    quality_from_metrics,
    serving_from_bench,
    serving_from_bench_report,
)


def test_quality_from_metrics_maps_finetune_keys():
    metrics = {
        "overall_pass_rate": 0.91,
        "grounded_citation_rate": 0.96,
        "refusal_accuracy": 0.94,
        "correct_citation_rate": 0.90,
        "hallucinated_citation_rate": 0.02,
        "false_refusal_rate": 0.06,
    }
    q = quality_from_metrics(metrics)
    assert q.overall_pass_rate == 0.91
    assert q.hallucinated_citation_rate == 0.02


def test_quality_missing_keys_default_zero():
    q = quality_from_metrics({"overall_pass_rate": 0.8})
    assert q.overall_pass_rate == 0.8
    assert q.refusal_accuracy == 0.0


def test_serving_from_bench_defaults():
    s = serving_from_bench({"output_tokens_per_s": 2200.0})
    assert s.output_tokens_per_s == 2200.0
    assert s.gpu == "A100-80GB"
    assert s.gpu_count == 1


def test_report_file_parsing(tmp_path):
    eval_report = tmp_path / "eval_report.json"
    eval_report.write_text(json.dumps({
        "base": {"overall_pass_rate": 0.70},
        "tuned": {"overall_pass_rate": 0.91, "grounded_citation_rate": 0.96},
    }), encoding="utf-8")
    q_tuned = quality_from_finetune_report(str(eval_report), which="tuned")
    q_base = quality_from_finetune_report(str(eval_report), which="base")
    assert q_tuned.overall_pass_rate == 0.91
    assert q_base.overall_pass_rate == 0.70

    bench = tmp_path / "bench.json"
    bench.write_text(json.dumps({
        "gpu": "H100-80GB", "gpu_usd_per_hr": 4.80, "output_tokens_per_s": 3100.0,
    }), encoding="utf-8")
    s = serving_from_bench_report(str(bench))
    assert s.gpu == "H100-80GB"
    assert s.output_tokens_per_s == 3100.0
