from __future__ import annotations

from app.schemas import JudgeReport, PatchProposal, SafetyReport, TestRun, Verdict


class SWEJudge:
    def evaluate(
        self,
        baseline_runs: tuple[TestRun, ...],
        patched_runs: tuple[TestRun, ...],
        patch: PatchProposal,
        safety: SafetyReport,
    ) -> JudgeReport:
        baseline_passed = bool(baseline_runs) and all(run.passed for run in baseline_runs)
        patched_passed = bool(patched_runs) and all(run.passed for run in patched_runs)
        regression_count = self._regression_count(baseline_runs, patched_runs)
        notes: list[str] = []
        if not patch.changed_files:
            notes.append("No patch was produced.")
        if safety.risk_score > 0:
            notes.append(f"Safety risk score: {safety.risk_score}.")
        if regression_count:
            notes.append(f"{regression_count} regression(s) detected.")
        if not baseline_passed and patched_passed and patch.changed_files and safety.allowed:
            verdict = Verdict.ACCEPT
            confidence = 0.88
        elif not safety.allowed:
            verdict = Verdict.UNSAFE
            confidence = 0.9
        elif patch.changed_files and not patched_passed:
            verdict = Verdict.NEEDS_FIX
            confidence = 0.72
        else:
            verdict = Verdict.INCONCLUSIVE
            confidence = 0.55
        return JudgeReport(
            verdict=verdict,
            confidence=confidence,
            baseline_passed=baseline_passed,
            patched_passed=patched_passed,
            regression_count=regression_count,
            notes=tuple(notes),
        )

    @staticmethod
    def _regression_count(baseline_runs: tuple[TestRun, ...], patched_runs: tuple[TestRun, ...]) -> int:
        baseline_by_name = {run.name: run for run in baseline_runs}
        count = 0
        for patched in patched_runs:
            baseline = baseline_by_name.get(patched.name)
            if baseline and baseline.passed and not patched.passed:
                count += 1
        return count
