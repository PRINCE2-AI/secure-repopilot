from __future__ import annotations

import sys
from pathlib import Path

from app.config import Settings, get_settings
from app.schemas import RepoProfile, TestCommand, relative_path


IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "dist", "build"}
LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
}
DEPENDENCY_FILES = {
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "package.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
}


class RepoAnalyzer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def analyze(self, repo_path: str | Path, issue_text: str = "") -> RepoProfile:
        root = Path(repo_path).resolve()
        files = self._collect_files(root)
        languages = sorted({LANGUAGE_BY_SUFFIX[path.suffix] for path in files if path.suffix in LANGUAGE_BY_SUFFIX})
        dependency_files = tuple(relative_path(path, root) for path in files if path.name in DEPENDENCY_FILES)
        important_files = tuple(self._rank_files(files, root, issue_text)[:20])
        test_commands = tuple(self._detect_test_commands(root, files))
        return RepoProfile(
            root=str(root),
            languages=tuple(languages),
            dependency_files=dependency_files,
            test_commands=test_commands,
            important_files=important_files,
            file_count=len(files),
        )

    def _collect_files(self, root: Path) -> list[Path]:
        files: list[Path] = []
        for path in root.rglob("*"):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if not path.is_file():
                continue
            if path.stat().st_size > self.settings.max_file_bytes:
                continue
            files.append(path)
            if len(files) >= self.settings.max_files_to_scan:
                break
        return files

    @staticmethod
    def _detect_test_commands(root: Path, files: list[Path]) -> list[TestCommand]:
        names = {path.name for path in files}
        rels = [relative_path(path, root) for path in files]
        commands: list[TestCommand] = []
        if "package.json" in names:
            commands.append(TestCommand(name="npm test", command=("npm", "test")))
        has_python_tests = any(rel.startswith("tests/") and path.name.startswith("test_") for path, rel in zip(files, rels))
        if has_python_tests:
            commands.append(TestCommand(name="python unittest", command=(sys.executable, "-m", "unittest", "discover", "-s", "tests")))
        if "pytest.ini" in names or "pyproject.toml" in names:
            commands.append(TestCommand(name="pytest", command=(sys.executable, "-m", "pytest", "-q")))
        if not commands and any(path.suffix == ".py" for path in files):
            commands.append(TestCommand(name="python compile", command=(sys.executable, "-m", "compileall", ".")))
        return commands

    @staticmethod
    def _rank_files(files: list[Path], root: Path, issue_text: str) -> list[str]:
        terms = {term.strip(".,:;()[]{}").lower() for term in issue_text.split() if len(term) > 3}
        ranked: list[tuple[int, str]] = []
        for path in files:
            rel = relative_path(path, root)
            score = 0
            lowered = rel.lower()
            if "/test" in lowered or lowered.startswith("test"):
                score += 1
            if path.suffix in {".py", ".js", ".ts"}:
                score += 2
            score += sum(3 for term in terms if term and term in lowered)
            ranked.append((score, rel))
        return [rel for _, rel in sorted(ranked, key=lambda item: (-item[0], item[1]))]
