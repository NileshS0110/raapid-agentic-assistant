
import pytest

from app.schemas import EmployeeRequest, RequestType
from app.router import route_request


@pytest.mark.parametrize(
    "question, expected_type",
    [
        (
            "What is the annual leave policy?",
            RequestType.POLICY
        ),
        (
            "How many leave days do I have?",
            RequestType.RECORD
        ),
        (
            "How many annual leave days do I have remaining?",
            RequestType.RECORD
        ),
        (
            "What is my reimbursement status?",
            RequestType.RECORD
        ),
        (
            "Raise a ticket for my laptop issue",
            RequestType.ACTION
        ),
        (
            "Update my bank details",
            RequestType.ACTION
        ),
        (
            "Hi",
            RequestType.CLARIFICATION
        )
    ]
)
def test_route_request(question, expected_type):

    request = EmployeeRequest(
        employee_id="EMP001",
        request_text=question
    )

    result = route_request(request)

    assert result.request_type == expected_type


def test_leave_balance_uses_record_tools():

    request = EmployeeRequest(
        employee_id="EMP001",
        request_text="How many annual leave days do I have remaining?"
    )

    result = route_request(request)

    assert result.request_type == RequestType.RECORD
    assert result.route == "record_tools"
