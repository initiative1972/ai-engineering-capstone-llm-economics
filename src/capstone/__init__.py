"""capstone-llm-economics — the integration flagship (#4 of 4).

This package answers one enterprise question with defensible numbers:

    "Should we self-host a fine-tuned open-weight model, or keep paying a
     closed API — on quality, cost, privacy and complexity?"

It consumes the *outputs* of the three sibling flagships:

  * domain-llm-finetune  -> quality metrics (grounded/citation/refusal)
  * llm-serving-bench     -> serving economics (throughput, A$/1M tokens)
  * multi-agent-prod      -> governance/trace posture (HITL, auditability)

...and turns them into a weighted four-axis decision plus a break-even
total-cost-of-ownership model. Every function here is pure and deterministic,
so the whole decision runs on CPU in CI with no GPU, no network, no secrets.
The *inputs* are illustrative/synthetic in this repo; real inputs come from
actually running the sibling repos on a GPU.
"""

__version__ = "0.1.0"
