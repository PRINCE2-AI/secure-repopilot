from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path

from app.config import Settings, get_settings
from app.schemas import TestCommand, TestRun


SAFE_ENV_KEYS = (
    "PATH",
    "PATHEXT",
    "COMSPEC",
    "SYSTEMROOT",
    "SYSTEMDRIVE",
    "WINDIR",
    "TEMP",
    "TMP",
    "HOME",
    "USERPROFILE",
    "VIRTUAL_ENV",
    "LANG",
    "LC_ALL",
)


class Tester:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def run(self, repo_root: str | Path, commands: tuple[TestCommand, ...]) -> tuple[TestRun, ...]:
        root = Path(repo_root)
        results: list[TestRun] = []
        for command in commands:
            started = time.perf_counter()
            cwd = root / command.cwd
            return_code, stdout, stderr = self._execute(command, cwd)
            duration_ms = round((time.perf_counter() - started) * 1000, 3)
            results.append(
                TestRun(
                    name=command.name,
                    command=command.display(),
                    passed=return_code == 0,
                    return_code=return_code,
                    stdout=stdout[-4000:],
                    stderr=stderr[-4000:],
                    duration_ms=duration_ms,
                )
            )
        return tuple(results)

    def _execute(self, command: TestCommand, cwd: Path) -> tuple[int, str, str]:
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        try:
            process = subprocess.Popen(
                list(command.command),
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._safe_env(),
                start_new_session=os.name != "nt",
                creationflags=creationflags,
            )
        except OSError as exc:
            return 127, "", f"{type(exc).__name__}: {exc}"

        try:
            stdout, stderr = process.communicate(timeout=self.settings.command_timeout_seconds)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            self._kill_tree(process)
            stdout, stderr = process.communicate()
            return 124, stdout, stderr

    @staticmethod
    def _safe_env() -> dict[str, str]:
        env = {key: os.environ[key] for key in SAFE_ENV_KEYS if key in os.environ}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    @staticmethod
    def _kill_tree(process: subprocess.Popen) -> None:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                capture_output=True,
                check=False,
            )
            return
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            process.kill()
