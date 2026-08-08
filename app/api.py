from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
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


@api.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "openai_enabled": settings.openai_enabled,
        "model": settings.openai_model,
        "database_path": str(settings.resolved_database_path),
    }


@api.post("/run-fullcycle")
def run_fullcycle(request: FullCycleRequest) -> dict[str, Any]:
    run = FullCycleRunner().run(
        request.repo_path,
        request.issue_text,
        apply_patch=request.apply_patch,
        workspace=request.workspace,
    )
    return run.to_dict()


@api.get("/runs")
def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    return FullCycleRunner().store.list_runs(limit=limit)


@api.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any] | None:
    return FullCycleRunner().store.get(run_id)


@api.get("/metrics/{run_id}")
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
