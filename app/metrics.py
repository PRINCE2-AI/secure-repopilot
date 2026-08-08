from __future__ import annotations

from app.schemas import FullCycleRun


def summarize_run(run: FullCycleRun) -> dict[str, float | str]:
    return {
        "verdict": run.judge.verdict.value,
        "confidence": run.judge.confidence,
        "safety_risk_score": run.safety.risk_score,
        "privacy_score": run.privacy.privacy_score,
        "leakage_count": float(run.privacy.leakage_count),
        "changed_file_count": float(len(run.patch.changed_files)),
        "baseline_passed": float(run.judge.baseline_passed),
        "patched_passed": float(run.judge.patched_passed),
        "regression_count": float(run.judge.regression_count),
    }
