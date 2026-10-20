"""In-memory async job stubs. Not Cloud Run Jobs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_JOBS: dict[str, dict[str, Any]] = {}


def create_job(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    job_id = str(uuid4())
    job = {
        "job_id": job_id,
        "kind": kind,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "result": None,
        "note": "local memory only; Cloud Run Jobs not connected (OPEN-12)",
    }
    _JOBS[job_id] = job
    return job


def get_job(job_id: str) -> dict[str, Any] | None:
    return _JOBS.get(job_id)


def complete_job(job_id: str, result: dict[str, Any]) -> dict[str, Any]:
    job = _JOBS[job_id]
    job["status"] = "succeeded"
    job["result"] = result
    return job
