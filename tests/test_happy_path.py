from src.support_assistant.prompting import build_user_message, load_system_prompt
from src.support_assistant.safety import inspect_question, inspect_response
from src.support_assistant.schemas import SupportResponse


def test_happy_path_question_is_allowed():
    decision = inspect_question("How can I create a stronger password?")
    assert decision["action"] == "allow"
    assert decision["kind"] == "none"


def test_happy_path_user_message_keeps_the_question():
    question = "How can I create a stronger password?"
    message = build_user_message(question)
    assert question in message
    assert "<customer_question>" in message


def test_happy_path_system_prompt_is_loaded():
    prompt = load_system_prompt()
    assert "Support Agent Assistant" in prompt
    assert "Version:" in prompt


def test_happy_path_model_output_is_allowed():
    response = SupportResponse.model_validate(
        {
            "answer": "Use a long, unique password that combines different types of characters and avoid reusing passwords from other accounts.",
            "confidence": "high",
            "actions": [
                {
                    "type": "none",
                    "description": "No additional support action is required.",
                }
            ],
        }
    )
    decision = inspect_response(response)
    assert decision["action"] == "allow"
