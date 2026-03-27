"""
AI Observability & Cost Intelligence Platform.
Real-time LLM monitoring: token costs, latency, drift detection, hallucination tracking.
"""
import logging
import time
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List
from openai import OpenAI
from anthropic import Anthropic
from app.core.config import settings

logger = logging.getLogger(__name__)

COST_TABLE = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.010, "output": 0.030},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
}

HALLUCINATION_CHECK_PROMPT = """Evaluate if this LLM response contains hallucinations or factual errors.

Question: {prompt}
Response: {response}

Respond with JSON only:
{{
  "hallucination_detected": true/false,
  "confidence": 0.0-1.0,
  "suspicious_claims": ["claim1", ...],
  "reasoning": "..."
}}"""

DRIFT_DETECTION_PROMPT = """Compare these two LLM responses to the same prompt.
Detect semantic drift or quality degradation.

Prompt: {prompt}
Baseline Response: {baseline}
Current Response: {current}

JSON response:
{{
  "drift_detected": true/false,
  "drift_score": 0.0-1.0,
  "quality_change": "improved|degraded|stable",
  "key_differences": [...],
  "recommendation": "..."
}}"""


class LLMCall:
    def __init__(self, call_id: str, model: str, prompt: str, response: str,
                 input_tokens: int, output_tokens: int, latency_ms: float, timestamp: str):
        self.call_id = call_id
        self.model = model
        self.prompt = prompt
        self.response = response
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.latency_ms = latency_ms
        self.timestamp = timestamp
        rates = COST_TABLE.get(model, {"input": 0.005, "output": 0.015})
        self.cost_usd = (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])

    def to_dict(self):
        return {
            "call_id": self.call_id,
            "model": self.model,
            "prompt": self.prompt[:200],
            "response": self.response[:300],
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": round(self.latency_ms, 1),
            "cost_usd": round(self.cost_usd, 6),
            "timestamp": self.timestamp,
        }


class ObservabilityService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._calls: List[LLMCall] = []
        self._baselines: dict = {}
        self._alerts: list = []

    def tracked_call(self, prompt: str, model: str = "gpt-4o", system: str = None, tags: dict = None) -> dict:
        call_id = str(uuid.uuid4())
        start = time.time()

        try:
            if "claude" in model:
                resp = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=system or "You are a helpful assistant.",
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = resp.content[0].text
                input_tokens = resp.usage.input_tokens
                output_tokens = resp.usage.output_tokens
            else:
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})
                resp = self.openai_client.chat.completions.create(model=model, messages=messages)
                response_text = resp.choices[0].message.content
                input_tokens = resp.usage.prompt_tokens
                output_tokens = resp.usage.completion_tokens

            latency_ms = (time.time() - start) * 1000
            call = LLMCall(call_id, model, prompt, response_text, input_tokens, output_tokens, latency_ms, datetime.utcnow().isoformat())
            self._calls.append(call)

            # Check alerts
            self._check_alerts(call)

            return {**call.to_dict(), "tags": tags or {}, "status": "success"}

        except Exception as exc:
            latency_ms = (time.time() - start) * 1000
            logger.error("LLM call failed: %s", exc)
            return {"call_id": call_id, "model": model, "error": str(exc), "latency_ms": round(latency_ms, 1), "status": "error"}

    def _check_alerts(self, call: LLMCall):
        if call.latency_ms > settings.LATENCY_ALERT_THRESHOLD_MS:
            self._alerts.append({
                "type": "latency",
                "severity": "warning",
                "message": f"High latency: {call.latency_ms:.0f}ms for model {call.model}",
                "call_id": call.call_id,
                "timestamp": datetime.utcnow().isoformat(),
            })
        total_cost = sum(c.cost_usd for c in self._calls)
        if total_cost > settings.COST_ALERT_THRESHOLD_USD:
            self._alerts.append({
                "type": "cost",
                "severity": "warning",
                "message": f"Cost threshold exceeded: ${total_cost:.4f} > ${settings.COST_ALERT_THRESHOLD_USD}",
                "timestamp": datetime.utcnow().isoformat(),
            })

    def detect_hallucinations(self, prompt: str, response: str) -> dict:
        check = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": HALLUCINATION_CHECK_PROMPT.format(prompt=prompt, response=response)}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        result = json.loads(check.choices[0].message.content)
        result["prompt"] = prompt[:200]
        result["response"] = response[:300]
        return result

    def detect_drift(self, prompt: str, current_response: str) -> dict:
        baseline = self._baselines.get(prompt[:100])
        if not baseline:
            self._baselines[prompt[:100]] = current_response
            return {"drift_detected": False, "message": "Baseline set. Run again to detect drift."}

        check = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": DRIFT_DETECTION_PROMPT.format(
                prompt=prompt, baseline=baseline[:500], current=current_response[:500]
            )}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        return json.loads(check.choices[0].message.content)

    def get_analytics(self, hours: int = 24) -> dict:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [c for c in self._calls if datetime.fromisoformat(c.timestamp) > cutoff]

        if not recent:
            return {"message": "No calls in the specified time range", "total_calls": 0}

        by_model = {}
        for call in recent:
            if call.model not in by_model:
                by_model[call.model] = {"calls": 0, "total_cost": 0, "total_tokens": 0, "avg_latency_ms": 0}
            by_model[call.model]["calls"] += 1
            by_model[call.model]["total_cost"] += call.cost_usd
            by_model[call.model]["total_tokens"] += call.input_tokens + call.output_tokens
            by_model[call.model]["avg_latency_ms"] += call.latency_ms

        for model in by_model:
            n = by_model[model]["calls"]
            by_model[model]["avg_latency_ms"] = round(by_model[model]["avg_latency_ms"] / n, 1)
            by_model[model]["total_cost"] = round(by_model[model]["total_cost"], 6)

        return {
            "period_hours": hours,
            "total_calls": len(recent),
            "total_cost_usd": round(sum(c.cost_usd for c in recent), 6),
            "total_tokens": sum(c.input_tokens + c.output_tokens for c in recent),
            "avg_latency_ms": round(sum(c.latency_ms for c in recent) / len(recent), 1),
            "p95_latency_ms": sorted([c.latency_ms for c in recent])[int(len(recent)*0.95)],
            "by_model": by_model,
            "active_alerts": len(self._alerts),
        }

    def get_calls(self, limit: int = 50) -> list:
        return [c.to_dict() for c in self._calls[-limit:]]

    def get_alerts(self) -> list:
        return self._alerts[-50:]

    def clear_alerts(self):
        self._alerts.clear()


_service: Optional[ObservabilityService] = None
def get_observability_service() -> ObservabilityService:
    global _service
    if _service is None:
        _service = ObservabilityService()
    return _service
