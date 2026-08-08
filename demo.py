from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.runner import FullCycleRunner


def main() -> None:
    root = Path(__file__).resolve().parent
    repo = root / "examples" / "buggy_python_repo"
    issue = (root / "data" / "sample_issues" / "divide_by_zero.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as workspace:
        run = FullCycleRunner().run(repo, issue, apply_patch=True, workspace=workspace)
        print(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "verdict": run.judge.verdict.value,
                    "confidence": run.judge.confidence,
                    "changed_files": run.patch.changed_files,
                    "baseline_passed": run.judge.baseline_passed,
                    "patched_passed": run.judge.patched_passed,
                    "safety_risk": run.safety.risk_score,
                    "privacy_score": run.privacy.privacy_score,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
