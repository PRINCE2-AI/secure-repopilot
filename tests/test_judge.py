from app.judge import SWEJudge
from app.schemas import PatchProposal, SafetyReport, TestRun, Verdict


def test_judge_accepts_failed_baseline_passing_patch() -> None:
    baseline = (TestRun("tests", "python -m unittest", False, 1, "", "", 10),)
    patched = (TestRun("tests", "python -m unittest", True, 0, "", "", 10),)
    patch = PatchProposal(("src/app.py",), "diff", True, "fix")
    safety = SafetyReport(True, 0.0)
    report = SWEJudge().evaluate(baseline, patched, patch, safety)
    assert report.verdict == Verdict.ACCEPT
