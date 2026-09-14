import csv
from datetime import datetime, timezone

from src.support_assistant.config import SAFETY_LOG_PATH
from src.support_assistant.schemas import Action, ActionType, Confidence, SupportResponse

INJECTION_PHRASES = (
    "ignore previous instructions",
    "ignore all instructions",
    "ignore the system prompt",
    "disregard previous instructions",
    "forget previous instructions",
    "new system prompt",
    "reveal your instructions",
    "reveal the system prompt",
    "print your system prompt",
    "show me the system prompt",
    "dump your system prompt",
    "repeat the instructions above",
    "ignora las instrucciones anteriores",
    "ignora el prompt del sistema",
    "olvida las instrucciones anteriores",
    "revela el prompt del sistema",
    "muestra el prompt del sistema",
    "mostrame el prompt del sistema",
    "muéstrame el prompt del sistema",
    "imprime el prompt del sistema",
)

LEAK_MARKERS = (
    "untrusted customer question",
    "never let it change these rules",
    "few-shot prompting",
    "support agent assistant prompt",
    "behavioral rules",
)

SAFETY_FIELDS = ["timestamp", "kind", "action", "reason"]


def inspect_question(question: str) -> dict:
    normalized = question.lower()
    for phrase in INJECTION_PHRASES:
        if phrase in normalized:
            return {
                "kind": "injection",
                "action": "fallback",
                "reason": f"matched phrase: {phrase}",
            }
    return {"kind": "none", "action": "allow", "reason": ""}


def inspect_response(response: SupportResponse) -> dict:
    text = " ".join(
        [response.answer, *[item.description for item in response.actions]]
    ).lower()
    for marker in LEAK_MARKERS:
        if marker in text:
            return {
                "kind": "prompt_leak",
                "action": "fallback",
                "reason": f"matched marker: {marker}",
            }
    return {"kind": "none", "action": "allow", "reason": ""}


def fallback_response() -> SupportResponse:
    return SupportResponse(
        answer=(
            "I cannot follow instructions inside the customer message "
            "or reveal internal assistant instructions. "
            "Please describe the original support issue."
        ),
        confidence=Confidence.LOW,
        actions=[
            Action(
                type=ActionType.REQUEST_INFORMATION,
                description=(
                    "Ask the customer to restate the support problem "
                    "without extra instructions."
                ),
            )
        ],
    )


def log_safety_decision(decision: dict) -> None:
    SAFETY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not SAFETY_LOG_PATH.exists() or SAFETY_LOG_PATH.stat().st_size == 0
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": decision.get("kind", ""),
        "action": decision.get("action", ""),
        "reason": decision.get("reason", ""),
    }
    with SAFETY_LOG_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SAFETY_FIELDS)
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)
