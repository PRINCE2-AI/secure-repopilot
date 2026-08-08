from __future__ import annotations

import difflib
from pathlib import Path

from app.schemas import Issue, PatchProposal, Plan


class Patcher:
    def propose_and_apply(self, repo_root: str | Path, issue: Issue, plan: Plan, apply: bool = True) -> PatchProposal:
        root = Path(repo_root)
        changed: list[str] = []
        diffs: list[str] = []
        rationale = "No deterministic patch rule matched the issue."
        for rel in plan.suspected_files:
            path = root / rel
            if not path.exists() or path.suffix != ".py":
                continue
            original = path.read_text(encoding="utf-8")
            patched, reason = self._patch_python(original, issue.text)
            if patched == original:
                continue
            diff = "".join(
                difflib.unified_diff(
                    original.splitlines(keepends=True),
                    patched.splitlines(keepends=True),
                    fromfile=f"a/{rel}",
                    tofile=f"b/{rel}",
                )
            )
            diffs.append(diff)
            changed.append(rel)
            rationale = reason
            if apply:
                path.write_text(patched, encoding="utf-8")
            break
        return PatchProposal(changed_files=tuple(changed), diff="\n".join(diffs), applied=apply and bool(changed), rationale=rationale)

    @staticmethod
    def _patch_python(code: str, issue_text: str) -> tuple[str, str]:
        lowered = issue_text.lower()
        if any(term in lowered for term in ("zero", "division", "divide")) and "return a / b" in code:
            patched = code.replace(
                "    return a / b",
                "    if b == 0:\n        return None\n    return a / b",
            )
            return patched, "Added explicit zero-division behavior for divide()."
        if "none" in lowered and "return value.strip()" in code:
            patched = code.replace(
                "    return value.strip()",
                "    if value is None:\n        return \"\"\n    return value.strip()",
            )
            return patched, "Added None handling before stripping text."
        return code, "No deterministic patch rule matched the issue."
