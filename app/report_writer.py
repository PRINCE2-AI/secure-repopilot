from __future__ import annotations

from app.schemas import FullCycleRun, TestRun


class ReportWriter:
    def write(self, run: FullCycleRun) -> str:
        return "\n".join(
            [
                f"# Secure RepoPilot Report: {run.issue.title}",
                "",
                f"**Verdict:** `{run.judge.verdict.value}`",
                f"**Confidence:** `{run.judge.confidence:.2f}`",
                f"**Safety risk:** `{run.safety.risk_score:.2f}`",
                f"**Privacy score:** `{run.privacy.privacy_score:.2f}`",
                "",
                "## Issue",
                run.issue.text,
                "",
                "## Plan",
                run.plan.summary,
                "",
                "## Changed Files",
                "\n".join(f"- `{path}`" for path in run.patch.changed_files) or "- No files changed",
                "",
                "## Baseline Tests",
                self._runs(run.reproduction.baseline_runs),
                "",
                "## Patched Tests",
                self._runs(run.patched_runs),
                "",
                "## Patch Rationale",
                run.patch.rationale,
                "",
                "## Risk Notes",
                "\n".join(f"- {note}" for note in run.judge.notes) or "- No judge warnings",
            ]
        )

    @staticmethod
    def _runs(runs: tuple[TestRun, ...]) -> str:
        if not runs:
            return "- No tests were run"
        lines = []
        for run in runs:
            status = "passed" if run.passed else "failed"
            lines.append(f"- `{run.name}`: {status} in {run.duration_ms:.0f} ms")
        return "\n".join(lines)
