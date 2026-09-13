from enum import Enum

from pydantic import BaseModel, Field


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
    type: ActionType
    description: str


class SupportResponse(BaseModel):
    answer: str
    confidence: Confidence
    actions: list[Action] = Field(min_length=1)
