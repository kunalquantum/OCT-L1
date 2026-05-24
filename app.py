"""CephMind web server — FastAPI backend + static UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from cephmind import CephMindOrchestrator, Query
from cephmind.agents import DEFAULT_AGENTS
from cephmind.core.models import AgentVerdict, ConsensusResult, ReasoningResult

app = FastAPI(title="CephMind", version="0.1.0")

_orchestrator = CephMindOrchestrator(DEFAULT_AGENTS)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ── request / response models ─────────────────────────────────────────────────

class ReasonRequest(BaseModel):
    text: str
    domain: str = "general"
    context: dict[str, Any] = {}


class VerdictOut(BaseModel):
    agent_name: str
    stance: str
    confidence: float
    summary: str
    findings: list[str]
    blockers: list[str]


class ConsensusOut(BaseModel):
    overall_stance: str
    confidence_score: float
    recommendation: str
    key_findings: list[str]
    major_blockers: list[str]
    dissenting_agents: list[str]


class ReasonResponse(BaseModel):
    verdicts: list[VerdictOut]
    consensus: ConsensusOut
    reliability_score: float


# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/reason", response_model=ReasonResponse)
def reason(req: ReasonRequest):
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="Query text must not be empty.")

    query = Query(text=req.text.strip(), domain=req.domain, context=req.context)
    result: ReasoningResult = _orchestrator.reason(query)

    return ReasonResponse(
        verdicts=[
            VerdictOut(
                agent_name=v.agent_name,
                stance=v.stance.value,
                confidence=v.confidence,
                summary=v.summary,
                findings=v.findings,
                blockers=v.blockers,
            )
            for v in result.verdicts
        ],
        consensus=ConsensusOut(
            overall_stance=result.consensus.overall_stance.value,
            confidence_score=result.consensus.confidence_score,
            recommendation=result.consensus.recommendation,
            key_findings=result.consensus.key_findings,
            major_blockers=result.consensus.major_blockers,
            dissenting_agents=result.consensus.dissenting_agents,
        ),
        reliability_score=result.reliability_score,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
