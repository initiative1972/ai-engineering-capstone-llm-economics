"""The committed reference scenario (synthetic, deterministic).

A mid-size regulated enterprise (a Tier-1 bank, in the abstract) runs a grounded
policy/compliance assistant. The question: keep paying a closed, GPT-4-class API,
or self-host the fine-tuned open-weight model from the sibling flagships?

Every number here is an *illustrative input*. The quality numbers have the shape
a ``domain-llm-finetune`` run would produce; the serving numbers have the shape a
``llm-serving-bench`` run would produce; the governance/complexity postures have
the shape a ``multi-agent-prod`` deployment review would produce. Swap any of
them for your own measured numbers — the engine does the rest.

No real data, no employer systems. Pure data; no model, no network.
"""
from __future__ import annotations

from dataclasses import dataclass

from .complexity import ComplexityProfile
from .economics import ClosedApiPricing, SelfHostServing, Workload
from .governance import GovernancePosture
from .quality import QualityProfile

CLOSED = "closed_api"
SELFHOST = "selfhost_tuned"


@dataclass
class OptionInputs:
    quality: QualityProfile
    governance: GovernancePosture
    complexity: ComplexityProfile


@dataclass
class Scenario:
    name: str
    workload: Workload
    closed_pricing: ClosedApiPricing
    selfhost_serving: SelfHostServing
    closed: OptionInputs
    selfhost: OptionInputs


def reference_scenario() -> Scenario:
    """The committed, deterministic reference case used by the demo and tests."""
    return Scenario(
        name="Tier-1 bank grounded compliance assistant",
        # ~1.5M requests/month, long policy context in, short grounded answer out.
        workload=Workload(
            requests_per_month=1_500_000,
            avg_input_tokens=800,
            avg_output_tokens=250,
        ),
        # Illustrative GPT-4-class list price (USD per 1M tokens).
        closed_pricing=ClosedApiPricing(
            usd_per_1m_input=2.50,
            usd_per_1m_output=10.00,
        ),
        # Illustrative vLLM serving of a quantised, fine-tuned 7-8B model.
        selfhost_serving=SelfHostServing(
            gpu="A100-80GB",
            gpu_count=1,
            gpu_usd_per_hr=3.20,
            output_tokens_per_s=2200.0,
            ops_aud_per_month=4000.0,     # partial SRE/MLOps time + monitoring
            reserved_hours_per_month=730.0,
        ),
        # Closed API: strong general quality, managed ops, but data leaves the
        # tenancy and the weights are opaque.
        closed=OptionInputs(
            quality=QualityProfile(
                overall_pass_rate=0.86,
                grounded_citation_rate=0.90,
                refusal_accuracy=0.82,
                correct_citation_rate=0.88,
                hallucinated_citation_rate=0.04,
                false_refusal_rate=0.10,
            ),
            governance=GovernancePosture(
                data_residency=0,
                pii_handling=1,
                auditability=1,
                access_control=1,
                model_transparency=0,
                low_vendor_lock_in=0,
                incident_recovery=1,
            ),
            complexity=ComplexityProfile(
                managed_ops=2,
                slo_headroom=2,
                team_readiness=2,
                small_blast_radius=1,
                upgrade_simplicity=2,
            ),
        ),
        # Self-hosted tuned model: beats the closed model on the *narrow* domain
        # trust metrics, keeps data in-tenancy with full traces, but you run it.
        selfhost=OptionInputs(
            quality=QualityProfile(
                overall_pass_rate=0.91,
                grounded_citation_rate=0.96,
                refusal_accuracy=0.94,
                correct_citation_rate=0.90,
                hallucinated_citation_rate=0.02,
                false_refusal_rate=0.06,
            ),
            governance=GovernancePosture(
                data_residency=2,
                pii_handling=2,
                auditability=2,
                access_control=2,
                model_transparency=2,
                low_vendor_lock_in=2,
                incident_recovery=2,
            ),
            complexity=ComplexityProfile(
                managed_ops=0,
                slo_headroom=1,
                team_readiness=1,
                small_blast_radius=1,
                upgrade_simplicity=1,
            ),
        ),
    )
