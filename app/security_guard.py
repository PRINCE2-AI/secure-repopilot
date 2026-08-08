from __future__ import annotations

import re
from pathlib import Path

from app.schemas import AuditFinding, SafetyReport, Severity, TestCommand


SECRET_PATTERNS = {
    "openai_key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "generic_secret": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
}
BLOCKED_COMMAND_TOKENS = {
    "curl",
    "wget",
    "ssh",
    "scp",
    "ftp",
    "powershell",
    "pwsh",
    "cmd",
    "rm",
    "rmdir",
    "del",
    "format",
    "shutdown",
}
ALLOWED_EXECUTABLE_HINTS = {"python", "pytest", "npm", "node"}


class SecurityGuard:
    def validate_commands(self, commands: tuple[TestCommand, ...]) -> SafetyReport:
        findings: list[AuditFinding] = []
        for command in commands:
            tokens = [Path(part).name.lower() for part in command.command]
            blocked = sorted(set(tokens) & BLOCKED_COMMAND_TOKENS)
            if blocked:
                findings.append(
                    AuditFinding(
                        check="command_policy",
                        severity=Severity.CRITICAL,
                        message=f"Blocked risky command token(s): {', '.join(blocked)}",
                        location=command.display(),
                    )
                )
            executable = tokens[0] if tokens else ""
            if not any(hint in executable for hint in ALLOWED_EXECUTABLE_HINTS):
                findings.append(
                    AuditFinding(
                        check="command_policy",
                        severity=Severity.MEDIUM,
                        message="Command is outside the default allow-list.",
                        location=command.display(),
                    )
                )
        return self._report(findings)

    def scan_text(self, text: str, location: str = "trace") -> SafetyReport:
        findings: list[AuditFinding] = []
        lowered = text.lower()
        if "ignore previous instructions" in lowered or "system prompt" in lowered:
            findings.append(
                AuditFinding(
                    check="prompt_injection",
                    severity=Severity.HIGH,
                    message="Possible prompt-injection instruction found in untrusted content.",
                    location=location,
                )
            )
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(
                    AuditFinding(
                        check="secret_detection",
                        severity=Severity.CRITICAL,
                        message=f"Possible secret detected: {name}",
                        location=location,
                    )
                )
        return self._report(findings)

    @staticmethod
    def _report(findings: list[AuditFinding]) -> SafetyReport:
        weights = {
            Severity.LOW: 0.1,
            Severity.MEDIUM: 0.25,
            Severity.HIGH: 0.55,
            Severity.CRITICAL: 1.0,
        }
        risk = min(1.0, sum(weights[finding.severity] for finding in findings))
        return SafetyReport(allowed=risk < 1.0 and not any(f.severity == Severity.CRITICAL for f in findings), risk_score=round(risk, 3), findings=tuple(findings))
