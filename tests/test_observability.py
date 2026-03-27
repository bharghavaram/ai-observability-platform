"""Tests for AI Observability Platform."""
import pytest
from unittest.mock import MagicMock, patch
from app.core.config import settings


def test_settings():
    assert settings.LATENCY_ALERT_THRESHOLD_MS == 5000
    assert settings.COST_ALERT_THRESHOLD_USD == 10.0
    assert settings.HALLUCINATION_THRESHOLD == 0.3


def test_cost_calculation():
    from app.services.observability_service import LLMCall, COST_TABLE
    call = LLMCall("id1", "gpt-4o", "prompt", "response", 1000, 500, 200.0, "2025-01-01T00:00:00")
    rates = COST_TABLE["gpt-4o"]
    expected_cost = (1000 / 1000 * rates["input"]) + (500 / 1000 * rates["output"])
    assert abs(call.cost_usd - expected_cost) < 1e-10


def test_llm_call_to_dict():
    from app.services.observability_service import LLMCall
    call = LLMCall("id1", "gpt-4o", "What is AI?", "AI is...", 100, 50, 1200.0, "2025-01-01T00:00:00")
    d = call.to_dict()
    assert d["call_id"] == "id1"
    assert d["model"] == "gpt-4o"
    assert d["latency_ms"] == 1200.0
    assert "cost_usd" in d


def test_get_analytics_empty():
    with patch("app.services.observability_service.OpenAI"), \
         patch("app.services.observability_service.Anthropic"):
        from app.services.observability_service import ObservabilityService
        svc = ObservabilityService()
        analytics = svc.get_analytics(hours=1)
        assert analytics["total_calls"] == 0


def test_get_calls_empty():
    with patch("app.services.observability_service.OpenAI"), \
         patch("app.services.observability_service.Anthropic"):
        from app.services.observability_service import ObservabilityService
        svc = ObservabilityService()
        calls = svc.get_calls()
        assert calls == []


def test_cost_table_coverage():
    from app.services.observability_service import COST_TABLE
    for model in ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet-20241022"]:
        assert model in COST_TABLE
        assert "input" in COST_TABLE[model]
        assert "output" in COST_TABLE[model]


@pytest.mark.asyncio
async def test_api_health():
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    resp = client.get("/api/v1/observe/health")
    assert resp.status_code == 200
