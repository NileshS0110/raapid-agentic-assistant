import json

from app.action_tools import (
    create_ticket,
    submit_for_human_review
)
from app.tools import ToolError


# Test 1: Successful ticket creation
def test_ticket_creation():

    result = create_ticket(
        session_employee_id="EMP001",
        title="Laptop is not starting",
        description="My laptop does not start when I press the power button.",
        category="IT Support",
        priority="High",
        request_id="REQ-001"
    )

    assert result["status"] == "success"
    assert result["data"]["employee_id"] == "EMP001"

    print("PASS: Ticket creation")


# Test 2: Duplicate request prevention
def test_duplicate_ticket():

    result = create_ticket(
        session_employee_id="EMP001",
        title="Laptop is not starting",
        description="My laptop does not start.",
        category="IT Support",
        priority="High",
        request_id="REQ-001"
    )

    assert result["duplicate_prevented"] is True

    print("PASS: Duplicate ticket prevention")


# Test 3: Missing ticket title
def test_missing_title():

    try:
        create_ticket(
            session_employee_id="EMP001",
            title="",
            description="My laptop does not start."
        )

    except ValueError:
        print("PASS: Missing title rejected")
        return

    raise AssertionError("Missing title was not rejected.")


# Test 4: Simulated ticketing system failure
def test_tool_failure():

    try:
        create_ticket(
            session_employee_id="EMP001",
            title="Keyboard issue",
            description="Some keys are not working.",
            simulate_failure=True
        )

    except ToolError:
        print("PASS: Tool failure handled")
        return

    raise AssertionError("Simulated tool failure was not detected.")


# Test 5: Human review submission
def test_human_review():

    result = submit_for_human_review(
        session_employee_id="EMP001",
        action_type="Update bank details",
        action_details={
            "requested_change": "Update salary account"
        },
        reason="Sensitive financial information change."
    )

    assert result["status"] == "pending_approval"

    print("PASS: Human approval workflow")


if __name__ == "__main__":

    tests = [
        test_ticket_creation,
        test_duplicate_ticket,
        test_missing_title,
        test_tool_failure,
        test_human_review
    ]

    for test in tests:
        try:
            test()

        except Exception as error:
            print(f"FAIL: {test.__name__}: {error}")