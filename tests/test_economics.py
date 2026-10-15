from capstone.economics import (
    ClosedApiPricing,
    SelfHostServing,
    Workload,
    break_even_requests_per_month,
    evaluate,
)


def _closed():
    return ClosedApiPricing(usd_per_1m_input=2.50, usd_per_1m_output=10.00)


def _selfhost():
    return SelfHostServing(
        gpu="A100-80GB", gpu_count=1, gpu_usd_per_hr=3.20,
        output_tokens_per_s=2200.0, ops_aud_per_month=4000.0,
        reserved_hours_per_month=730.0,
    )


def _workload():
    return Workload(requests_per_month=1_500_000, avg_input_tokens=800,
                    avg_output_tokens=250)


def test_closed_cost_per_request():
    per_req = _closed().aud_per_request(800, 250)
    assert round(per_req, 5) == 0.00684


def test_selfhost_fixed_cost():
    fixed = _selfhost().fixed_aud_per_month()
    # GPU 3.20*1.52*730 + ops 4000
    assert round(fixed, 2) == 7550.72


def test_break_even_matches_fixed_over_per_request():
    be = break_even_requests_per_month(_closed(), _selfhost(), 800, 250)
    assert round(be) == 1_103_906


def test_evaluate_recommends_selfhost_at_volume():
    r = evaluate(_closed(), _selfhost(), _workload())
    assert round(r.monthly_cost_closed_aud, 2) == 10260.0
    assert round(r.monthly_cost_selfhost_aud, 2) == 7550.72
    assert r.cheaper_option == "selfhost"
    assert round(r.monthly_saving_aud, 2) == 2709.28
    assert r.over_capacity is False
    assert r.effective_aud_per_1m_tokens_selfhost < \
        r.effective_aud_per_1m_tokens_closed


def test_low_volume_favours_closed():
    small = Workload(requests_per_month=100_000, avg_input_tokens=800,
                     avg_output_tokens=250)
    r = evaluate(_closed(), _selfhost(), small)
    assert r.cheaper_option == "closed"


def test_no_break_even_when_free_api():
    free = ClosedApiPricing(usd_per_1m_input=0.0, usd_per_1m_output=0.0)
    assert break_even_requests_per_month(free, _selfhost(), 800, 250) is None


def test_over_capacity_flag():
    tiny_gpu = SelfHostServing(
        gpu="L4", gpu_count=1, gpu_usd_per_hr=0.80,
        output_tokens_per_s=1.0, reserved_hours_per_month=730.0,
    )
    r = evaluate(_closed(), tiny_gpu, _workload())
    assert r.over_capacity is True
