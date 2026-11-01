from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RequestType(str, Enum):
    POLICY = "policy_question"
    RECORD = "record_query"
    ACTION = "action_request"
    CLARIFICATION = "clarification_required"


class EmployeeRequest(BaseModel):
    employee_id: Optional[str] = None
    request_text: str = Field(min_length=1)


class RouteResult(BaseModel):
    request_type: RequestType
    route: str
    reason: str
    requires_human_review: bool = False
    clarification_question: Optional[str] = None