import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_MODEL = "gpt-4o-mini"
METRICS_PATH = PROJECT_ROOT / "metrics" / "metrics.csv"
SAFETY_LOG_PATH = PROJECT_ROOT / "metrics" / "safety.csv"

MODEL_PRICES_PER_MILLION = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


class ConfigurationError(Exception):
    """Raised when required environment configuration is missing."""


def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your API key."
        )
    return api_key


def get_openai_model() -> str:
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip()
    return model or DEFAULT_MODEL
