# run_capstone.py

**Path:** `scripts/run_capstone.py`

End-to-end capstone demo (offline, deterministic, no GPU).

Runs the reference scenario under every weight profile, writes the decision record (markdown), a machine-readable `last_run.json`, and a break-even SVG, then prints a short summary. Exit code `0` means the pipeline ran and produced a recommendation.

```python
#!/usr/bin/env python3
"""End-to-end capstone demo (offline, deterministic, no GPU).

Runs the reference scenario under every weight profile, writes the decision
record (markdown), a machine-readable last_run.json, and a break-even SVG, then
prints a short summary. Exit code 0 means the pipeline ran and produced a
recommendation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from capstone import pipeline, report                 # noqa: E402
from capstone.chart import breakeven_svg              # noqa: E402
from capstone.config import DEFAULT_PROFILE, REPORTS_DIR, WEIGHT_PROFILES  # noqa: E402
from capstone.scenario import reference_scenario      # noqa: E402


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    profile = argv[0] if argv else DEFAULT_PROFILE

    scenario = reference_scenario()

    # Decision under the chosen profile for the record...
    result = pipeline.run(scenario, profile)

    # ...and under every profile for the sensitivity table.
    sensitivity = {
        p: pipeline.run(scenario, p).decision.winner.name
        for p in WEIGHT_PROFILES
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md = report.render_markdown(result, sensitivity)
    (REPORTS_DIR / "decision_record.md").write_text(md, encoding="utf-8")

    payload = result.as_dict()
    payload["sensitivity"] = sensitivity
    (REPORTS_DIR / "last_run.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    per_request = scenario.closed_pricing.aud_per_request(
        scenario.workload.avg_input_tokens, scenario.workload.avg_output_tokens
    )
    svg = breakeven_svg(
        per_request_aud=per_request,
        fixed_selfhost_aud=scenario.selfhost_serving.fixed_aud_per_month(),
        break_even_requests=result.economics.break_even_requests_per_month,
        current_requests=scenario.workload.requests_per_month,
    )
    (REPORTS_DIR / "breakeven.svg").write_text(svg, encoding="utf-8")

    ec = result.economics
    dec = result.decision
    print(f"scenario            : {result.scenario_name}")
    print(f"profile             : {profile}")
    print(f"recommendation      : {dec.winner.name}")
    print(f"deciding axis       : {dec.deciding_axis}")
    print(f"closed  A$/mo       : {ec.monthly_cost_closed_aud:,.0f}")
    print(f"selfhost A$/mo      : {ec.monthly_cost_selfhost_aud:,.0f}")
    if ec.break_even_requests_per_month is not None:
        print(f"break-even req/mo   : {ec.break_even_requests_per_month:,.0f}")
    print(f"cheaper now         : {ec.cheaper_option} "
          f"(saves A${ec.monthly_saving_aud:,.0f}/mo)")
    print(f"sensitivity         : {sensitivity}")
    print(f"wrote               : {REPORTS_DIR / 'decision_record.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
