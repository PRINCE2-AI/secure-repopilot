from pathlib import Path

import pytest
from fastapi import HTTPException

from app import api as api_module
from app.config import Settings


def test_require_api_token_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(api_token=""))

    with pytest.raises(HTTPException) as exc:
        api_module.require_api_token(None)

    assert exc.value.status_code == 503


def test_require_api_token_rejects_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(api_token="s3cret"))

    with pytest.raises(HTTPException) as exc:
        api_module.require_api_token("wrong")

    assert exc.value.status_code == 401


def test_require_api_token_accepts_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(api_token="s3cret"))

    assert api_module.require_api_token("s3cret") is None


def test_resolve_repo_path_blocks_outside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repos"
    root.mkdir()
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(repo_root=root))

    with pytest.raises(HTTPException) as exc:
        api_module.resolve_repo_path(str(tmp_path / "outside"))

    assert exc.value.status_code == 400


def test_resolve_repo_path_allows_inside_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repos"
    repo = root / "project"
    repo.mkdir(parents=True)
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(repo_root=root))

    assert api_module.resolve_repo_path(str(repo)) == repo.resolve()


def test_resolve_repo_path_resolves_relative_to_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repos"
    repo = root / "project"
    repo.mkdir(parents=True)
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(repo_root=root))

    assert api_module.resolve_repo_path("project") == repo.resolve()


def test_resolve_repo_path_blocks_relative_escape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repos"
    root.mkdir()
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(repo_root=root))

    with pytest.raises(HTTPException) as exc:
        api_module.resolve_repo_path("../outside")

    assert exc.value.status_code == 400


def test_resolve_repo_path_fails_closed_without_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_module, "get_settings", lambda: Settings(repo_root=None))

    with pytest.raises(HTTPException) as exc:
        api_module.resolve_repo_path(".")

    assert exc.value.status_code == 503
