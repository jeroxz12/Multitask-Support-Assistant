import time

from openai import OpenAI
from pydantic import ValidationError

from src.support_assistant.config import get_openai_api_key, get_openai_model
from src.support_assistant.prompting import build_user_message, load_system_prompt
from src.support_assistant.schemas import SupportResponse


class ResponseValidationError(Exception):
    """Raised when the model output does not match SupportResponse."""

    def __init__(self, message: str, usage: dict | None = None) -> None:
        super().__init__(message)
        self.usage = usage or {}


def generate_support_response(question: str) -> tuple[SupportResponse, dict]:
    model = get_openai_model()
    client = OpenAI(api_key=get_openai_api_key())
    started = time.perf_counter()
    api_response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": load_system_prompt()},
            {"role": "user", "content": build_user_message(question)},
        ],
        text_format=SupportResponse,
    )
    latency_ms = (time.perf_counter() - started) * 1000
    usage = _usage_from_response(model, api_response, latency_ms)

    parsed = api_response.output_parsed
    if parsed is None:
        raise ResponseValidationError(
            "The model did not return a valid SupportResponse.",
            usage=usage,
        )

    try:
        response = SupportResponse.model_validate(parsed.model_dump())
    except ValidationError as exc:
        raise ResponseValidationError(
            f"The model response failed schema validation: {exc}",
            usage=usage,
        ) from exc

    return response, usage


def _usage_from_response(model: str, api_response: object, latency_ms: float) -> dict:
    usage = getattr(api_response, "usage", None)
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", 0) or 0)
    if total_tokens <= 0:
        total_tokens = input_tokens + output_tokens
    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
    }
