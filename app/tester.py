from __future__ import annotations

import subprocess
import time
from pathlib import Path

from app.config import Settings, get_settings
from app.schemas import TestCommand, TestRun


class Tester:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def run(self, repo_root: str | Path, commands: tuple[TestCommand, ...]) -> tuple[TestRun, ...]:
        root = Path(repo_root)
        results: list[TestRun] = []
        for command in commands:
            started = time.perf_counter()
            cwd = root / command.cwd
            try:
                completed = subprocess.run(
                    list(command.command),
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=self.settings.command_timeout_seconds,
                )
                duration_ms = round((time.perf_counter() - started) * 1000, 3)
                results.append(
                    TestRun(
                        name=command.name,
                        command=command.display(),
                        passed=completed.returncode == 0,
                        return_code=completed.returncode,
                        stdout=completed.stdout[-4000:],
                        stderr=completed.stderr[-4000:],
                        duration_ms=duration_ms,
                    )
                )
            except subprocess.TimeoutExpired as exc:
                duration_ms = round((time.perf_counter() - started) * 1000, 3)
                results.append(
                    TestRun(
                        name=command.name,
                        command=command.display(),
                        passed=False,
                        return_code=124,
                        stdout=str(exc.stdout or "")[-4000:],
                        stderr=str(exc.stderr or "")[-4000:],
                        duration_ms=duration_ms,
                    )
                )
        return tuple(results)
