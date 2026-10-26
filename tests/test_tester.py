import sys
from pathlib import Path

from app.config import Settings
from app.schemas import TestCommand
from app.tester import Tester


def test_safe_env_drops_secrets(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-should-not-leak")
    monkeypatch.setenv("REPOPILOT_API_TOKEN", "token-should-not-leak")

    env = Tester._safe_env()

    assert "OPENAI_API_KEY" not in env
    assert "REPOPILOT_API_TOKEN" not in env
    assert "PATH" in env


def test_tester_runs_command_with_scrubbed_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-should-not-leak")
    code = "import os; print(os.getenv('OPENAI_API_KEY', 'missing'))"

    results = Tester(Settings(command_timeout_seconds=10)).run(
        tmp_path,
        (TestCommand("env-check", (sys.executable, "-c", code)),),
    )

    assert results[0].passed
    assert "missing" in results[0].stdout
    assert "sk-should-not-leak" not in results[0].stdout
