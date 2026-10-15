# ADR 0002 — A fixed-vs-variable break-even cost model

## Status
Accepted.

## Context
The money question is not "what is the GPU per hour?" but "at our volume, which
option is cheaper, and where is the crossover?". The two options have
fundamentally different cost shapes:

- **Closed API** — near-pure *variable* cost: A$ per token, scaling linearly
  with volume, forever.
- **Self-host** — mostly *fixed* cost: a reserved GPU plus the engineering/ops
  time to run it, paid whether or not a request arrives; the marginal token cost
  on an already-reserved GPU is small.

## Decision
Model monthly cost as:

```
closed(v)   = v * per_request_price           # variable
selfhost(v) = gpu_reservation + ops           # fixed
break_even  = fixed / per_request_price        # crossover volume
```

Also report the **effective A$/1M output tokens at the actual volume** for each
option (fixed cost spread over real tokens), because that is the unit the
sibling `llm-serving-bench` repo speaks in, and it shows the self-host unit price
falling as volume rises. Finally, compute the **capacity** of the reserved GPUs
(throughput × seconds/month) and flag when demand exceeds it (you must scale).

## Consequences
- A clean, defensible "break-even volume" story instead of a single number.
- Honest about ops cost: self-hosting is not just GPU rental.
- Deliberately **excludes** one-off migration/build effort and treats marginal
  token cost as ≈ 0 — both stated as caveats in the report. Add them as inputs
  if your context needs them.
- GPU prices and the FX rate are illustrative inputs, overridable per provider.
