from app.schemas import (
    EmployeeRequest,
    RouteResult,
    RequestType
)


# Keywords indicating an employee wants an action
ACTION_KEYWORDS = [
    "raise a ticket",
    "create a ticket",
    "open a ticket",
    "update my",
    "change my",
    "escalate",
    "submit a request",
    "report an issue"
]


# Keywords indicating a query about structured employee records
RECORD_KEYWORDS = [
    # Leave balance
    "leave balance",
    "remaining leave",
    "leave days remaining",
    "annual leave remaining",
    "annual leave days",
    "how many leave days do i have",
    "how many annual leave days do i have",
    "how many leave days have i got",
    "how many leaves",
    "how much leave",
    "my leave",
    "leave days do i have",

    # Reimbursements
    "reimbursement status",
    "expense status",
    "reimbursement claim",

    # Assets
    "assigned asset",
    "my laptop",
    "my equipment",
    "asset assigned"
]


def route_request(request: EmployeeRequest) -> RouteResult:

    text = request.request_text.lower().strip()

    # 1. Handle empty or extremely vague requests
    if len(text) < 5:
        return RouteResult(
            request_type=RequestType.CLARIFICATION,
            route="clarification",
            reason="Request is too short to identify the intent.",
            clarification_question="Could you describe what you need help with?"
        )

    # 2. Deterministic action routing
    if any(keyword in text for keyword in ACTION_KEYWORDS):
        return RouteResult(
            request_type=RequestType.ACTION,
            route="action_workflow",
            reason="Request contains an action-related keyword."
        )

    # 3. Deterministic record query routing
    if any(keyword in text for keyword in RECORD_KEYWORDS):
        return RouteResult(
            request_type=RequestType.RECORD,
            route="record_tools",
            reason="Request contains a structured-record keyword."
        )

    # 4. Default to policy knowledge retrieval
    return RouteResult(
        request_type=RequestType.POLICY,
        route="policy_rag",
        reason="Request does not match a structured record or action rule."
    )
