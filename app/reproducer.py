from __future__ import annotations

from pathlib import Path

from app.schemas import ReproductionResult, RepoProfile
from app.tester import Tester


class Reproducer:
    def __init__(self, tester: Tester | None = None) -> None:
        self.tester = tester or Tester()

    def reproduce(self, repo_root: str | Path, profile: RepoProfile) -> ReproductionResult:
        runs = self.tester.run(repo_root, profile.test_commands)
        reproduced = any(not run.passed for run in runs)
        if reproduced:
            evidence = "At least one baseline command fails before patching."
        elif runs:
            evidence = "Baseline commands pass; issue may require a targeted regression test."
        else:
            evidence = "No test command detected."
        return ReproductionResult(reproduced=reproduced, baseline_runs=runs, evidence=evidence)
