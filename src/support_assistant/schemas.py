from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionType(str, Enum):
    NONE = "none"
    REQUEST_INFORMATION = "request_information"
    TROUBLESHOOT = "troubleshoot"
    ESCALATE_HUMAN = "escalate_human"
    FOLLOW_UP = "follow_up"


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ActionType
    description: str

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be empty or whitespace")
        return value


class SupportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    confidence: Confidence
    actions: list[Action] = Field(min_length=1)

    @field_validator("answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("answer cannot be empty or whitespace")
        return value
