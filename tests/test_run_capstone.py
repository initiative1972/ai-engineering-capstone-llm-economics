import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    path = ROOT / "scripts" / "run_capstone.py"
    spec = importlib.util.spec_from_file_location("run_capstone", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_runs_and_writes_artifacts():
    module = _load_script()
    rc = module.main([])
    assert rc == 0
    reports = ROOT / "reports"
    assert (reports / "decision_record.md").exists()
    assert (reports / "last_run.json").exists()
    assert (reports / "breakeven.svg").exists()


def test_demo_accepts_a_profile_argument():
    module = _load_script()
    assert module.main(["cost_sensitive_startup"]) == 0
