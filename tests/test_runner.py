from pathlib import Path

from app.runner import FullCycleRunner


def test_full_cycle_runner_fixes_sample_repo(tmp_path) -> None:
    root = Path(__file__).resolve().parents[1]
    repo = root / "examples" / "buggy_python_repo"
    issue = (root / "data" / "sample_issues" / "divide_by_zero.md").read_text(encoding="utf-8")
    run = FullCycleRunner().run(repo, issue, apply_patch=True, workspace=tmp_path)
    assert run.judge.verdict.value == "accept"
    assert not run.judge.baseline_passed
    assert run.judge.patched_passed
    assert "src/securecalc/calculator.py" in run.patch.changed_files
