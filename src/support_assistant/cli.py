import sys
import time

from openai import APIError, AuthenticationError

from src.support_assistant.config import ConfigurationError, get_openai_model
from src.support_assistant.llm import ResponseValidationError, generate_support_response
from src.support_assistant.metrics import persist_run
from src.support_assistant.safety import (
    fallback_response,
    inspect_question,
    inspect_response,
    log_safety_decision,
)

USAGE = 'Usage: python -m src.support_assistant "<question>"'


def parse_question(argv: list[str]) -> str:
    if len(argv) != 2 or not argv[1].strip():
        raise ValueError(USAGE)
    return argv[1].strip()


def main() -> None:
    status = "error"
    usage = {
        "model": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "latency_ms": 0.0,
    }
    result_json = None
    started = time.perf_counter()

    try:
        question = parse_question(sys.argv)
        usage["model"] = get_openai_model()
        result_json, status, usage = _run_query(question, usage)
    except ValueError as exc:
        status = "invalid_usage"
        print(str(exc), file=sys.stderr)
    except ConfigurationError as exc:
        status = "configuration_error"
        print(f"Configuration error: {exc}", file=sys.stderr)
    except ResponseValidationError as exc:
        status = "validation_error"
        if exc.usage:
            usage = exc.usage
        print(f"Validation error: {exc}", file=sys.stderr)
    except AuthenticationError:
        status = "authentication_error"
        print("Authentication failed. Check that OPENAI_API_KEY is valid.", file=sys.stderr)
    except APIError as exc:
        status = "api_error"
        print(f"OpenAI API error: {exc}", file=sys.stderr)

    latency_ms = usage.get("latency_ms") or (time.perf_counter() - started) * 1000
    _write_metrics(status, usage, latency_ms)

    if result_json is not None:
        print(result_json)
        sys.exit(0)
    sys.exit(1)


def _run_query(question: str, usage: dict) -> tuple[str, str, dict]:
    input_decision = inspect_question(question)
    if input_decision["action"] == "fallback":
        _write_safety(input_decision)
        return fallback_response().model_dump_json(indent=2), "safety_block", usage

    result, usage = generate_support_response(question)
    output_decision = inspect_response(result)
    if output_decision["action"] == "fallback":
        _write_safety(output_decision)
        return fallback_response().model_dump_json(indent=2), "safety_fallback", usage

    return result.model_dump_json(indent=2), "success", usage


def _write_metrics(status: str, usage: dict, latency_ms: float) -> None:
    try:
        persist_run(
            status=status,
            model=usage.get("model") or "",
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
            latency_ms=latency_ms,
        )
    except OSError as exc:
        print(f"Failed to write metrics: {exc}", file=sys.stderr)


def _write_safety(decision: dict) -> None:
    try:
        log_safety_decision(decision)
    except OSError as exc:
        print(f"Failed to write safety log: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
