"""AI Observability Platform – API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.observability_service import ObservabilityService, get_observability_service

router = APIRouter(prefix="/observe", tags=["AI Observability"])

class TrackedCallRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o"
    system: Optional[str] = None
    tags: Optional[dict] = None

class HallucinationRequest(BaseModel):
    prompt: str
    response: str

class DriftRequest(BaseModel):
    prompt: str
    current_response: str

@router.post("/call")
async def tracked_call(req: TrackedCallRequest, svc: ObservabilityService = Depends(get_observability_service)):
    return svc.tracked_call(req.prompt, req.model, req.system, req.tags)

@router.post("/hallucination")
async def detect_hallucinations(req: HallucinationRequest, svc: ObservabilityService = Depends(get_observability_service)):
    return svc.detect_hallucinations(req.prompt, req.response)

@router.post("/drift")
async def detect_drift(req: DriftRequest, svc: ObservabilityService = Depends(get_observability_service)):
    return svc.detect_drift(req.prompt, req.current_response)

@router.get("/analytics")
async def get_analytics(hours: int = 24, svc: ObservabilityService = Depends(get_observability_service)):
    return svc.get_analytics(hours)

@router.get("/calls")
async def get_calls(limit: int = 50, svc: ObservabilityService = Depends(get_observability_service)):
    return {"calls": svc.get_calls(limit)}

@router.get("/alerts")
async def get_alerts(svc: ObservabilityService = Depends(get_observability_service)):
    return {"alerts": svc.get_alerts()}

@router.delete("/alerts")
async def clear_alerts(svc: ObservabilityService = Depends(get_observability_service)):
    svc.clear_alerts()
    return {"message": "Alerts cleared"}

@router.get("/health")
async def health():
    return {"status": "ok", "service": "AI Observability & Cost Intelligence Platform"}
