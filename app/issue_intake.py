from __future__ import annotations

import re

from app.schemas import Issue


GITHUB_ISSUE_PATTERN = re.compile(r"https://github\.com/([^/\s]+)/([^/\s]+)/issues/(\d+)")


class IssueIntake:
    def parse(self, raw: str) -> Issue:
        text = raw.strip()
        match = GITHUB_ISSUE_PATTERN.search(text)
        source = match.group(0) if match else "local"
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0] if lines else "Untitled issue"
        body = "\n".join(lines[1:]) if len(lines) > 1 else text
        labels = self._classify_labels(text)
        return Issue(title=title, body=body, source=source, labels=labels)

    @staticmethod
    def _classify_labels(text: str) -> tuple[str, ...]:
        lowered = text.lower()
        labels: list[str] = []
        if any(word in lowered for word in ("traceback", "exception", "crash", "error")):
            labels.append("runtime-error")
        if any(word in lowered for word in ("wrong", "incorrect", "expected", "actual")):
            labels.append("wrong-output")
        if any(word in lowered for word in ("test", "regression", "failing")):
            labels.append("test-related")
        if any(word in lowered for word in ("security", "secret", "token", "privacy")):
            labels.append("security")
        return tuple(labels or ["bug"])
