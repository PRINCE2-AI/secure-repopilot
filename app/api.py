from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any

try:
    from fastapi import Depends, FastAPI, Header, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install API dependencies with `pip install -r requirements.txt`.") from exc

from app.config import get_settings
from app.runner import FullCycleRunner


class FullCycleRequest(BaseModel):
    repo_path: str
    issue_text: str
    apply_patch: bool = Field(default=True)
    workspace: str | None = Field(default=None)


api = FastAPI(
    title="Secure RepoPilot",
    description="SWE-Cycle-inspired issue-to-PR coding agent with verification, safety, and privacy auditing.",
    version="0.1.0",
)


def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    expected = get_settings().api_token
    if not expected:
        raise HTTPException(status_code=503, detail="REPOPILOT_API_TOKEN is not configured")
    if not secrets.compare_digest(x_api_token or "", expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API token")


def resolve_repo_path(raw: str) -> Path:
    root = get_settings().resolved_repo_root
    if root is None:
        raise HTTPException(status_code=503, detail="REPOPILOT_REPO_ROOT is not configured")
    candidate = Path(raw).expanduser()
    path = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        inside = os.path.commonpath([os.path.normcase(str(path)), os.path.normcase(str(root))]) == os.path.normcase(str(root))
    except ValueError:
        inside = False
    if not inside:
        raise HTTPException(status_code=400, detail=f"Path is outside REPOPILOT_REPO_ROOT: {raw}")
    return path


@api.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "openai_enabled": settings.openai_enabled,
        "model": settings.openai_model,
        "database_path": str(settings.resolved_database_path),
    }


@api.post("/run-fullcycle", dependencies=[Depends(require_api_token)])
def run_fullcycle(request: FullCycleRequest) -> dict[str, Any]:
    settings = get_settings()
    repo_path = resolve_repo_path(request.repo_path)
    workspace = resolve_repo_path(request.workspace) if request.workspace else settings.resolved_repo_root / ".repopilot-runs"
    run = FullCycleRunner().run(
        repo_path,
        request.issue_text,
        apply_patch=request.apply_patch,
        workspace=workspace,
    )
    return run.to_dict()


@api.get("/runs", dependencies=[Depends(require_api_token)])
def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    return FullCycleRunner().store.list_runs(limit=limit)


@api.get("/runs/{run_id}", dependencies=[Depends(require_api_token)])
def get_run(run_id: str) -> dict[str, Any] | None:
    return FullCycleRunner().store.get(run_id)


@api.get("/metrics/{run_id}", dependencies=[Depends(require_api_token)])
def metrics(run_id: str) -> dict[str, Any]:
    payload = FullCycleRunner().store.get(run_id)
    if not payload:
        return {"error": "run not found"}
    return {
        "verdict": payload["judge"]["verdict"],
        "confidence": payload["judge"]["confidence"],
        "safety_risk_score": payload["safety"]["risk_score"],
        "privacy_score": payload["privacy"]["privacy_score"],
        "changed_file_count": len(payload["patch"]["changed_files"]),
    }
