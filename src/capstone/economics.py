"""Cost axis — the break-even / total-cost-of-ownership engine.

The honest shape of the "self-host vs closed API" money question is
**fixed vs variable cost**:

  * A closed API is almost pure *variable* cost: you pay per token, forever.
  * Self-hosting is mostly *fixed* cost: you reserve a GPU (and pay engineers to
    run it) whether or not a request arrives; the marginal token cost is small.

So there is a **break-even monthly volume** above which self-hosting is cheaper.
Below it, the closed API wins. This module computes that crossover, the monthly
cost of each option at a given volume, and the *effective* unit price (A$/1M
tokens) at that volume — which is what makes the serving-bench numbers legible.

Serving economics (GPU A$/hr and tokens/s -> A$/1M tokens) follow the same model
as the sibling ``llm-serving-bench`` repo. All prices are illustrative inputs.

Pure functions only.
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import DEFAULT_USD_AUD, SECONDS_PER_MONTH


@dataclass
class ClosedApiPricing:
    """Per-token list price for a closed, hosted API (illustrative)."""

    usd_per_1m_input: float
    usd_per_1m_output: float
    usd_aud: float = DEFAULT_USD_AUD

    def aud_per_request(self, input_tokens: int, output_tokens: int) -> float:
        aud_in = self.usd_per_1m_input * self.usd_aud / 1_000_000
        aud_out = self.usd_per_1m_output * self.usd_aud / 1_000_000
        return input_tokens * aud_in + output_tokens * aud_out


@dataclass
class SelfHostServing:
    """A self-hosted serving configuration (shape mirrors llm-serving-bench)."""

    gpu: str
    gpu_count: int
    gpu_usd_per_hr: float
    output_tokens_per_s: float          # measured throughput from the bench
    ops_aud_per_month: float = 0.0      # engineering/monitoring overhead, amortised
    reserved_hours_per_month: float = 730.0  # 24/7 by default
    usd_aud: float = DEFAULT_USD_AUD

    def gpu_aud_per_month(self) -> float:
        hourly = self.gpu_usd_per_hr * self.gpu_count * self.usd_aud
        return hourly * self.reserved_hours_per_month

    def fixed_aud_per_month(self) -> float:
        """GPU reservation + ops — paid regardless of volume."""
        return self.gpu_aud_per_month() + self.ops_aud_per_month

    def capacity_requests_per_month(self, output_tokens: int) -> float:
        """How many requests the reserved GPUs can serve in a month."""
        if output_tokens <= 0:
            return float("inf")
        total_output_tokens = self.output_tokens_per_s * SECONDS_PER_MONTH
        return total_output_tokens / output_tokens


@dataclass
class Workload:
    """The monthly demand being priced."""

    requests_per_month: int
    avg_input_tokens: int
    avg_output_tokens: int

    def output_tokens_per_month(self) -> int:
        return self.requests_per_month * self.avg_output_tokens


@dataclass
class EconomicsResult:
    monthly_cost_closed_aud: float
    monthly_cost_selfhost_aud: float
    break_even_requests_per_month: float | None
    cheaper_option: str
    monthly_saving_aud: float
    selfhost_capacity_requests_per_month: float
    over_capacity: bool
    effective_aud_per_1m_tokens_closed: float
    effective_aud_per_1m_tokens_selfhost: float | None

    def as_dict(self) -> dict:
        return {
            "monthly_cost_closed_aud": round(self.monthly_cost_closed_aud, 2),
            "monthly_cost_selfhost_aud": round(self.monthly_cost_selfhost_aud, 2),
            "break_even_requests_per_month": (
                None if self.break_even_requests_per_month is None
                else round(self.break_even_requests_per_month)
            ),
            "cheaper_option": self.cheaper_option,
            "monthly_saving_aud": round(self.monthly_saving_aud, 2),
            "selfhost_capacity_requests_per_month": round(
                self.selfhost_capacity_requests_per_month
            ),
            "over_capacity": self.over_capacity,
            "effective_aud_per_1m_tokens_closed": round(
                self.effective_aud_per_1m_tokens_closed, 2
            ),
            "effective_aud_per_1m_tokens_selfhost": (
                None if self.effective_aud_per_1m_tokens_selfhost is None
                else round(self.effective_aud_per_1m_tokens_selfhost, 2)
            ),
        }


def break_even_requests_per_month(
    closed: ClosedApiPricing,
    selfhost: SelfHostServing,
    avg_input_tokens: int,
    avg_output_tokens: int,
) -> float | None:
    """Volume where closed variable cost equals self-host fixed cost.

    Returns ``None`` when there is no crossover (the closed per-request price is
    zero or negative, so self-hosting never catches up).
    """
    per_request = closed.aud_per_request(avg_input_tokens, avg_output_tokens)
    if per_request <= 0:
        return None
    return selfhost.fixed_aud_per_month() / per_request


def evaluate(
    closed: ClosedApiPricing,
    selfhost: SelfHostServing,
    workload: Workload,
) -> EconomicsResult:
    """Full economics at a given monthly volume."""
    per_request = closed.aud_per_request(
        workload.avg_input_tokens, workload.avg_output_tokens
    )
    monthly_closed = per_request * workload.requests_per_month

    # Self-host is dominated by fixed cost; marginal token cost ~ 0 on a
    # reserved GPU, so we model monthly self-host cost as the fixed cost.
    monthly_selfhost = selfhost.fixed_aud_per_month()

    be = break_even_requests_per_month(
        closed, selfhost, workload.avg_input_tokens, workload.avg_output_tokens
    )

    capacity = selfhost.capacity_requests_per_month(workload.avg_output_tokens)
    over_capacity = workload.requests_per_month > capacity

    if monthly_selfhost < monthly_closed:
        cheaper = "selfhost"
        saving = monthly_closed - monthly_selfhost
    else:
        cheaper = "closed"
        saving = monthly_selfhost - monthly_closed

    out_tokens = workload.output_tokens_per_month()
    eff_closed = (
        monthly_closed / out_tokens * 1_000_000 if out_tokens else 0.0
    )
    eff_selfhost = (
        monthly_selfhost / out_tokens * 1_000_000 if out_tokens else None
    )

    return EconomicsResult(
        monthly_cost_closed_aud=monthly_closed,
        monthly_cost_selfhost_aud=monthly_selfhost,
        break_even_requests_per_month=be,
        cheaper_option=cheaper,
        monthly_saving_aud=saving,
        selfhost_capacity_requests_per_month=capacity,
        over_capacity=over_capacity,
        effective_aud_per_1m_tokens_closed=eff_closed,
        effective_aud_per_1m_tokens_selfhost=eff_selfhost,
    )
