from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from app.config import Settings, get_settings
from app.issue_intake import IssueIntake
from app.judge import SWEJudge
from app.patcher import Patcher
from app.planner import Planner
from app.privacy_auditor import PrivacyAuditor
from app.repo_analyzer import RepoAnalyzer
from app.report_writer import ReportWriter
from app.reproducer import Reproducer
from app.schemas import FullCycleRun
from app.security_guard import SecurityGuard
from app.storage import RunStore
from app.tester import Tester


class FullCycleRunner:
    def __init__(self, settings: Settings | None = None, store: RunStore | None = None) -> None:
        self.settings = settings or get_settings()
        self.intake = IssueIntake()
        self.analyzer = RepoAnalyzer(self.settings)
        self.planner = Planner()
        self.guard = SecurityGuard()
        self.tester = Tester(self.settings)
        self.reproducer = Reproducer(self.tester)
        self.patcher = Patcher()
        self.judge = SWEJudge()
        self.privacy = PrivacyAuditor()
        self.writer = ReportWriter()
        self.store = store or RunStore(self.settings.resolved_database_path)

    def run(self, repo_path: str | Path, issue_text: str, apply_patch: bool = True, workspace: str | Path | None = None) -> FullCycleRun:
        run_id = uuid.uuid4().hex[:12]
        source_repo = Path(repo_path).resolve()
        workspace_to_use = workspace
        if workspace_to_use is None and apply_patch:
            workspace_to_use = source_repo.parent / ".repopilot-runs"
        working_repo = self._prepare_workspace(source_repo, run_id, workspace_to_use)
        issue = self.intake.parse(issue_text)
        profile = self.analyzer.analyze(working_repo, issue.text)
        plan = self.planner.create_plan(issue, profile)
        command_safety = self.guard.validate_commands(profile.test_commands)
        issue_safety = self.guard.scan_text(issue.text, location="issue")
        safety = self._merge_safety(command_safety, issue_safety)
        reproduction = self.reproducer.reproduce(working_repo, profile)
        patch = self.patcher.propose_and_apply(working_repo, issue, plan, apply=apply_patch and safety.allowed)
        patched_runs = self.tester.run(working_repo, profile.test_commands) if patch.applied else ()
        diff_safety = self.guard.scan_text(patch.diff, location="patch.diff")
        safety = self._merge_safety(safety, diff_safety)
        trace = (
            {"event": "issue", "title": issue.title, "labels": issue.labels},
            {"event": "plan", "suspected_files": plan.suspected_files},
            {"event": "patch", "changed_files": patch.changed_files, "applied": patch.applied},
            {"event": "tests", "baseline": [run.passed for run in reproduction.baseline_runs], "patched": [run.passed for run in patched_runs]},
        )
        privacy = self.privacy.audit_trace(trace)
        judge = self.judge.evaluate(reproduction.baseline_runs, patched_runs, patch, safety)
        placeholder = FullCycleRun(
            run_id=run_id,
            repo_profile=profile,
            issue=issue,
            plan=plan,
            reproduction=reproduction,
            patch=patch,
            patched_runs=patched_runs,
            safety=safety,
            privacy=privacy,
            judge=judge,
            report_markdown="",
            trace=trace,
        )
        report = self.writer.write(placeholder)
        final = FullCycleRun(
            run_id=run_id,
            repo_profile=profile,
            issue=issue,
            plan=plan,
            reproduction=reproduction,
            patch=patch,
            patched_runs=patched_runs,
            safety=safety,
            privacy=privacy,
            judge=judge,
            report_markdown=report,
            trace=trace,
        )
        self.store.save(final)
        return final

    @staticmethod
    def _prepare_workspace(repo_path: Path, run_id: str, workspace: str | Path | None) -> Path:
        source = repo_path.resolve()
        if workspace is None:
            return source
        target_root = Path(workspace).resolve()
        target = target_root / f"repopilot-{run_id}"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        return target

    @staticmethod
    def _merge_safety(*reports):
        findings = tuple(finding for report in reports for finding in report.findings)
        risk = min(1.0, sum(report.risk_score for report in reports))
        allowed = all(report.allowed for report in reports)
        from app.schemas import SafetyReport

        return SafetyReport(allowed=allowed, risk_score=round(risk, 3), findings=findings)
