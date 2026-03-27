import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_observability")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    COST_PER_1K_INPUT_GPT4: float = float(os.getenv("COST_PER_1K_INPUT_GPT4", "0.005"))
    COST_PER_1K_OUTPUT_GPT4: float = float(os.getenv("COST_PER_1K_OUTPUT_GPT4", "0.015"))
    COST_PER_1K_INPUT_CLAUDE: float = float(os.getenv("COST_PER_1K_INPUT_CLAUDE", "0.003"))
    COST_PER_1K_OUTPUT_CLAUDE: float = float(os.getenv("COST_PER_1K_OUTPUT_CLAUDE", "0.015"))
    LATENCY_ALERT_THRESHOLD_MS: int = int(os.getenv("LATENCY_ALERT_THRESHOLD_MS", "5000"))
    COST_ALERT_THRESHOLD_USD: float = float(os.getenv("COST_ALERT_THRESHOLD_USD", "10.0"))
    HALLUCINATION_THRESHOLD: float = float(os.getenv("HALLUCINATION_THRESHOLD", "0.3"))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

settings = Settings()
