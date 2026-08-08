from __future__ import annotations

from app.schemas import Issue, Plan, PlanStep, RepoProfile, Severity


class Planner:
    def create_plan(self, issue: Issue, profile: RepoProfile) -> Plan:
        suspected = self._suspected_files(issue, profile)
        risk = Severity.HIGH if "security" in issue.labels else Severity.MEDIUM
        steps = (
            PlanStep("baseline", "Run the detected test command before changing code.", suspected),
            PlanStep("localize", "Inspect ranked files and identify the smallest likely fix.", suspected),
            PlanStep("patch", "Apply a minimal patch and avoid unrelated refactors.", suspected),
            PlanStep("verify", "Run the same tests after the patch and compare against baseline.", suspected),
            PlanStep("audit", "Scan commands, diffs, logs, and final report for safety/privacy issues.", suspected),
        )
        return Plan(
            summary=f"Resolve issue with {len(suspected)} suspected file(s) and baseline-aware verification.",
            suspected_files=suspected,
            risk_level=risk,
            steps=steps,
        )

    @staticmethod
    def _suspected_files(issue: Issue, profile: RepoProfile) -> tuple[str, ...]:
        issue_terms = issue.text.lower()
        matches = [path for path in profile.important_files if any(part in issue_terms for part in path.lower().replace("_", " ").split("/"))]
        if matches:
            return tuple(matches[:5])
        return tuple(profile.important_files[:5])
