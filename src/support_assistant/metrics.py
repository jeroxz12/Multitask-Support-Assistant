import csv
from datetime import datetime, timezone

from src.support_assistant.config import METRICS_PATH, MODEL_PRICES_PER_MILLION

FIELDNAMES = [
    "timestamp",
    "status",
    "model",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "latency_ms",
    "estimated_cost_usd",
]


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    prices = MODEL_PRICES_PER_MILLION.get(model)
    if prices is None:
        return 0.0
    return (
        input_tokens * prices["input"] + output_tokens * prices["output"]
    ) / 1_000_000


def persist_run(
    *,
    status: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    latency_ms: float,
) -> None:
    if total_tokens <= 0:
        total_tokens = input_tokens + output_tokens

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency_ms, 2),
        "estimated_cost_usd": f"{estimate_cost_usd(model, input_tokens, output_tokens):.8f}",
    }
    _append_csv(row)


def _append_csv(row: dict) -> None:
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not METRICS_PATH.exists() or METRICS_PATH.stat().st_size == 0
    with METRICS_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)
