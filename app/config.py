from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[1]
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    database_path: Path = Path(os.getenv("REPOPILOT_DB_PATH", "data/repopilot.db"))
    command_timeout_seconds: float = float(os.getenv("REPOPILOT_COMMAND_TIMEOUT", "8"))
    max_files_to_scan: int = int(os.getenv("REPOPILOT_MAX_FILES", "250"))
    max_file_bytes: int = int(os.getenv("REPOPILOT_MAX_FILE_BYTES", "120000"))
    api_token: str = field(default_factory=lambda: os.getenv("REPOPILOT_API_TOKEN", ""))
    repo_root: Path | None = field(
        default_factory=lambda: Path(os.environ["REPOPILOT_REPO_ROOT"]) if os.getenv("REPOPILOT_REPO_ROOT") else None
    )

    @property
    def resolved_database_path(self) -> Path:
        if self.database_path.is_absolute():
            return self.database_path
        return self.project_root / self.database_path

    @property
    def resolved_repo_root(self) -> Path | None:
        if self.repo_root is None:
            return None
        if self.repo_root.is_absolute():
            return self.repo_root.resolve()
        return (self.project_root / self.repo_root).resolve()

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key)


def get_settings() -> Settings:
    return Settings()
