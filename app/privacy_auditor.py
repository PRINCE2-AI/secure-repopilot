from __future__ import annotations

import re
from typing import Any

from app.schemas import AuditFinding, PrivacyReport, Severity


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
WINDOWS_PRIVATE_PATH_RE = re.compile(r"C:\\Users\\[^\\\s]+\\[^\s]+", re.IGNORECASE)
TOKEN_RE = re.compile(r"(?i)\b(token|api[_-]?key|password|secret)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}")


class PrivacyAuditor:
    def audit_trace(self, trace: tuple[dict[str, Any], ...]) -> PrivacyReport:
        findings: list[AuditFinding] = []
        for index, event in enumerate(trace):
            text = str(event)
            location = f"trace[{index}]"
            if EMAIL_RE.search(text):
                findings.append(AuditFinding("email_leakage", Severity.MEDIUM, "Email-like value appears in trace.", location))
            if WINDOWS_PRIVATE_PATH_RE.search(text):
                findings.append(AuditFinding("local_path_leakage", Severity.LOW, "Local user path appears in trace.", location))
            if TOKEN_RE.search(text):
                findings.append(AuditFinding("secret_leakage", Severity.CRITICAL, "Secret-like value appears in trace.", location))
        leakage_count = len(findings)
        penalty = min(1.0, sum(0.15 if f.severity == Severity.LOW else 0.35 if f.severity == Severity.MEDIUM else 1.0 for f in findings))
        return PrivacyReport(privacy_score=round(1.0 - penalty, 3), leakage_count=leakage_count, findings=tuple(findings))
