from pydantic import ValidationError
import pytest

from src.support_assistant.schemas import SupportResponse

HAPPY_PATH_PAYLOAD = {
    "answer": "Use a long, unique password that combines different types of characters and avoid reusing passwords from other accounts.",
    "confidence": "high",
    "actions": [
        {
            "type": "none",
            "description": "No additional support action is required.",
        }
    ],
}


def test_valid_support_response_is_accepted():
    response = SupportResponse.model_validate(HAPPY_PATH_PAYLOAD)
    assert response.confidence.value == "high"
    assert response.actions[0].type.value == "none"
    assert response.answer


def test_valid_response_serializes_to_json():
    response = SupportResponse.model_validate(HAPPY_PATH_PAYLOAD)
    json_text = response.model_dump_json()
    parsed = SupportResponse.model_validate_json(json_text)
    assert parsed == response


def test_invalid_confidence_is_rejected():
    payload = {**HAPPY_PATH_PAYLOAD, "confidence": "maybe"}
    with pytest.raises(ValidationError):
        SupportResponse.model_validate(payload)


def test_empty_actions_are_rejected():
    payload = {**HAPPY_PATH_PAYLOAD, "actions": []}
    with pytest.raises(ValidationError):
        SupportResponse.model_validate(payload)


def test_missing_answer_is_rejected():
    payload = {
        "confidence": "high",
        "actions": HAPPY_PATH_PAYLOAD["actions"],
    }
    with pytest.raises(ValidationError):
        SupportResponse.model_validate(payload)
