from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Verdict(str, Enum):
    ACCEPT = "accept"
    NEEDS_FIX = "needs_fix"
    UNSAFE = "unsafe"
    INCONCLUSIVE = "inconclusive"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TestCommand:
    name: str
    command: tuple[str, ...]
    cwd: str = "."

    def display(self) -> str:
        return " ".join(self.command)


@dataclass(frozen=True)
class RepoProfile:
    root: str
    languages: tuple[str, ...]
    dependency_files: tuple[str, ...]
    test_commands: tuple[TestCommand, ...]
    important_files: tuple[str, ...]
    file_count: int


@dataclass(frozen=True)
class Issue:
    title: str
    body: str
    source: str = "local"
    labels: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return f"{self.title}\n\n{self.body}".strip()


@dataclass(frozen=True)
class PlanStep:
    name: str
    detail: str
    target_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class Plan:
    summary: str
    suspected_files: tuple[str, ...]
    risk_level: Severity
    steps: tuple[PlanStep, ...]


@dataclass(frozen=True)
class TestRun:
    name: str
    command: str
    passed: bool
    return_code: int
    stdout: str
    stderr: str
    duration_ms: float


@dataclass(frozen=True)
class ReproductionResult:
    reproduced: bool
    baseline_runs: tuple[TestRun, ...]
    evidence: str


@dataclass(frozen=True)
class PatchProposal:
    changed_files: tuple[str, ...]
    diff: str
    applied: bool
    rationale: str


@dataclass(frozen=True)
class AuditFinding:
    check: str
    severity: Severity
    message: str
    location: str = ""


@dataclass(frozen=True)
class SafetyReport:
    allowed: bool
    risk_score: float
    findings: tuple[AuditFinding, ...] = ()


@dataclass(frozen=True)
class PrivacyReport:
    privacy_score: float
    leakage_count: int
    findings: tuple[AuditFinding, ...] = ()


@dataclass(frozen=True)
class JudgeReport:
    verdict: Verdict
    confidence: float
    baseline_passed: bool
    patched_passed: bool
    regression_count: int
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FullCycleRun:
    run_id: str
    repo_profile: RepoProfile
    issue: Issue
    plan: Plan
    reproduction: ReproductionResult
    patch: PatchProposal
    patched_runs: tuple[TestRun, ...]
    safety: SafetyReport
    privacy: PrivacyReport
    judge: JudgeReport
    report_markdown: str
    trace: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["judge"]["verdict"] = self.judge.verdict.value
        data["plan"]["risk_level"] = self.plan.risk_level.value
        for report_key in ("safety", "privacy"):
            for finding in data[report_key]["findings"]:
                finding["severity"] = finding["severity"].value
        return data


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)
