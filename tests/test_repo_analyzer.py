from pathlib import Path

from app.repo_analyzer import RepoAnalyzer


def test_repo_analyzer_detects_python_sample() -> None:
    root = Path(__file__).resolve().parents[1]
    profile = RepoAnalyzer().analyze(root / "examples" / "buggy_python_repo", "division by zero calculator")
    assert "Python" in profile.languages
    assert profile.test_commands
    assert any("calculator.py" in path for path in profile.important_files)
