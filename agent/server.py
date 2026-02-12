"""FastAPI server exposing the brand intelligence workflow as an API.

Also serves the React frontend as static files in production so the
entire app runs as a single Railway service.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.config import AgentConfig
from agent.models import BrandQuery, TaskStatus
from agent.utils.logging import get_logger
from agent.workflows.brand_intelligence import BrandIntelligenceWorkflow

logger = get_logger("server")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Brand Intelligence Agent API",
    description="Autonomous brand and competitor intelligence using Firecrawl, Tavily, Playwright, and DataForSEO",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (swap for Redis/DB in production)
_jobs: dict[str, dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class BrandQueryRequest(BaseModel):
    brand_name: str = Field(..., description="The brand name to analyze")
    website_url: str = Field(..., description="The brand's primary website URL")
    industry: str = Field("", description="Industry or vertical")
    known_competitors: list[str] = Field(default_factory=list, description="Known competitor domains")
    target_keywords: list[str] = Field(default_factory=list, description="Target SEO keywords")
    social_profiles: dict[str, str] = Field(default_factory=dict, description="Known social profile URLs")
    depth: str = Field("comprehensive", description="Analysis depth: quick, standard, comprehensive")


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    started_at: str
    completed_at: str | None = None
    report_path: str | None = None
    html_report_path: str | None = None
    errors: list[str] = []
    tasks_completed: int = 0
    tasks_total: int = 5

# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "brand-intelligence-agent"}


@app.post("/api/analyze", response_model=JobResponse)
async def start_analysis(request: BrandQueryRequest) -> JobResponse:
    """Start a new brand intelligence analysis (runs in background)."""
    job_id = str(uuid.uuid4())[:8]

    query = BrandQuery(
        brand_name=request.brand_name,
        website_url=request.website_url,
        industry=request.industry,
        known_competitors=request.known_competitors,
        target_keywords=request.target_keywords,
        social_profiles=request.social_profiles,
        depth=request.depth,
    )

    _jobs[job_id] = {
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "report_path": None,
        "html_report_path": None,
        "errors": [],
        "tasks_completed": 0,
        "query": query,
        "brand_name": request.brand_name,
        "website_url": request.website_url,
    }

    asyncio.create_task(_run_job(job_id, query))

    logger.info("Job %s started for %s", job_id, request.brand_name)
    return JobResponse(
        job_id=job_id,
        status="running",
        message=f"Analysis started for {request.brand_name}. Poll /api/status/{job_id} for progress.",
    )


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str) -> JobStatusResponse:
    """Check the status of a running analysis job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = _jobs[job_id]
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        started_at=job["started_at"],
        completed_at=job.get("completed_at"),
        report_path=job.get("report_path"),
        html_report_path=job.get("html_report_path"),
        errors=job.get("errors", []),
        tasks_completed=job.get("tasks_completed", 0),
    )


@app.get("/api/jobs")
async def list_jobs() -> list[dict[str, Any]]:
    """List all jobs with summary info."""
    return [
        {
            "job_id": jid,
            "status": j["status"],
            "started_at": j["started_at"],
            "completed_at": j.get("completed_at"),
            "brand_name": j.get("brand_name", ""),
            "website_url": j.get("website_url", ""),
            "report_path": j.get("report_path"),
            "html_report_path": j.get("html_report_path"),
        }
        for jid, j in _jobs.items()
    ]


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str) -> dict[str, str]:
    """Delete a job from the dashboard."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    del _jobs[job_id]
    logger.info("Job %s deleted", job_id)
    return {"status": "deleted", "job_id": job_id}


@app.get("/api/reports/{job_id}/html")
async def get_html_report(job_id: str) -> FileResponse:
    """Serve the HTML report for a completed job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = _jobs[job_id]
    html_path = job.get("html_report_path")

    if not html_path:
        raise HTTPException(status_code=404, detail="HTML report not found for this job")

    html_file = Path(html_path)
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="HTML report file does not exist")

    return FileResponse(
        html_file,
        media_type="text/html",
        filename=html_file.name
    )


@app.get("/api/reports/{job_id}/markdown")
async def get_markdown_report(job_id: str) -> FileResponse:
    """Serve the Markdown report for a completed job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = _jobs[job_id]
    report_path = job.get("report_path")

    if not report_path:
        raise HTTPException(status_code=404, detail="Markdown report not found for this job")

    report_file = Path(report_path)
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Markdown report file does not exist")

    return FileResponse(
        report_file,
        media_type="text/markdown",
        filename=report_file.name
    )


# ---------------------------------------------------------------------------
# Background job runner
# ---------------------------------------------------------------------------

async def _run_job(job_id: str, query: BrandQuery) -> None:
    """Execute the workflow and update job state."""
    try:
        config = AgentConfig(output_dir=Path("./reports"))
        workflow = BrandIntelligenceWorkflow(config)
        await workflow.initialize()

        state = await workflow.run(query)

        _jobs[job_id]["status"] = state.status.value
        _jobs[job_id]["completed_at"] = state.completed_at
        _jobs[job_id]["report_path"] = state.report_path
        _jobs[job_id]["html_report_path"] = getattr(state, 'html_report_path', None)
        _jobs[job_id]["errors"] = state.errors
        _jobs[job_id]["tasks_completed"] = sum(
            1 for t in state.task_results if t.status == TaskStatus.COMPLETED
        )

    except Exception as exc:
        logger.error("Job %s failed: %s", job_id, exc, exc_info=True)
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        _jobs[job_id]["errors"] = [str(exc)]


# ---------------------------------------------------------------------------
# Static file serving — React SPA
# ---------------------------------------------------------------------------

DIST_DIR = Path(__file__).resolve().parent.parent / "dist"


@app.on_event("startup")
async def _mount_frontend() -> None:
    """Mount the built React app if the dist directory exists."""
    if DIST_DIR.is_dir():
        # Serve /assets/* directly
        assets = DIST_DIR / "assets"
        if assets.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")
        logger.info("Serving frontend from %s", DIST_DIR)
    else:
        logger.warning("No frontend build found at %s — run `npm run build` first", DIST_DIR)


@app.get("/{full_path:path}", response_model=None)
async def serve_spa(request: Request, full_path: str) -> FileResponse | HTMLResponse:
    """Catch-all: serve static files or fall back to index.html for SPA routing."""
    # Try to serve an exact file match first (favicon, robots.txt, etc.)
    file_path = DIST_DIR / full_path
    if file_path.is_file():
        return FileResponse(file_path)

    # Fall back to index.html for client-side routing
    index = DIST_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)

    return HTMLResponse(
        content="<h1>Frontend not built</h1><p>Run <code>npm run build</code> then restart the server.</p>",
        status_code=200,
    )
