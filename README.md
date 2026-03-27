> **📅 Project Period:** Nov 2024 – Dec 2024 &nbsp;|&nbsp; **Status:** Completed &nbsp;|&nbsp; **Author:** [Bharghava Ram Vemuri](https://github.com/bharghavaram)

# AI Observability & Cost Intelligence Platform

> Real-time LLM monitoring with token cost tracking, hallucination detection, drift alerting, and multi-model analytics

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude-orange)](https://anthropic.com)

## Overview

As LLM applications scale to production, monitoring becomes critical. This platform provides **real-time observability** for any LLM-powered application — tracking costs, latency, quality, and safety metrics across OpenAI and Anthropic models.

## Why This Matters

- GPT-4 API costs can spiral without tracking (a single misconfigured prompt costs 100x more)
- Response quality degrades silently (model drift, hallucinations) without automated detection
- No standard tooling exists for cross-model performance comparison

## Architecture

```
LLM Calls → Tracked Wrapper → Metrics Store
                ↓
        ┌───────────────────┐
        │  Cost Calculator  │ → Real-time cost by model
        │  Latency Tracker  │ → P50/P95 latency analytics
        │  Hallucination    │ → Judge-LLM evaluation
        │  Drift Detector   │ → Baseline comparison
        └───────────────────┘
                ↓
        Alerts + Analytics Dashboard
```

## Key Features

- **Per-call cost tracking** – exact USD cost for every GPT-4o, Claude, and Mistral call
- **Latency percentiles** – P50/P95 latency monitoring with threshold alerts
- **Hallucination detection** – judge-LLM evaluates factual accuracy of responses
- **Drift detection** – compares responses against baselines to detect quality degradation
- **Multi-model analytics** – compare GPT-4o vs Claude vs GPT-3.5 side by side
- **Configurable alerts** – cost and latency threshold notifications

## Quick Start

```bash
git clone https://github.com/bharghavaram/ai-observability-platform
cd ai-observability-platform
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/observe/call` | Make a tracked LLM call |
| POST | `/api/v1/observe/hallucination` | Check for hallucinations |
| POST | `/api/v1/observe/drift` | Detect response drift |
| GET | `/api/v1/observe/analytics` | Cost + latency analytics |
| GET | `/api/v1/observe/calls` | Recent call history |
| GET | `/api/v1/observe/alerts` | Active alerts |

### Example: Tracked Call

```bash
curl -X POST "http://localhost:8000/api/v1/observe/call" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain transformer attention",
    "model": "gpt-4o",
    "tags": {"feature": "search", "user_id": "u123"}
  }'
```

### Example: Analytics Response

```json
{
  "period_hours": 24,
  "total_calls": 142,
  "total_cost_usd": 3.47,
  "avg_latency_ms": 1820.3,
  "p95_latency_ms": 4200.0,
  "by_model": {
    "gpt-4o": {"calls": 98, "total_cost": 2.94, "avg_latency_ms": 2100.0},
    "gpt-4o-mini": {"calls": 44, "total_cost": 0.53, "avg_latency_ms": 890.0}
  }
}
```

## Cost Reference Table

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| GPT-4o | $0.005 | $0.015 |
| GPT-4o-mini | $0.00015 | $0.0006 |
| Claude 3.5 Sonnet | $0.003 | $0.015 |
| Claude 3 Haiku | $0.00025 | $0.00125 |
