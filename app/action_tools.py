import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.tools import authorize_employee, ToolError


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_records(filename):
    """Read records from a JSON file."""

    path = DATA_DIR / filename

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        raise ToolError(f"Unable to read action data: {filename}")


def save_records(filename, records):
    """Save records to a JSON file."""

    path = DATA_DIR / filename

    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=2)

    except OSError:
        raise ToolError(f"Unable to save action data: {filename}")


def create_ticket(
    session_employee_id,
    title,
    description,
    category="General",
    priority="Medium",
    request_id=None,
    simulate_failure=False
):
    """
    Create a support ticket for an authenticated employee.

    request_id provides basic duplicate-request protection.
    """

    authorize_employee(session_employee_id, session_employee_id)

    if not title or not title.strip():
        raise ValueError("Ticket title is required.")

    if not description or not description.strip():
        raise ValueError("Ticket description is required.")

    allowed_priorities = ["Low", "Medium", "High", "Critical"]

    if priority not in allowed_priorities:
        raise ValueError("Invalid ticket priority.")

    # Simulate an unavailable ticketing system
    if simulate_failure:
        raise ToolError("Ticketing system is temporarily unavailable.")

    tickets = load_records("tickets.json")

    # Prevent duplicate processing of the same request
    if request_id:
        existing_ticket = next(
            (
                ticket for ticket in tickets
                if ticket["request_id"] == request_id
            ),
            None
        )

        if existing_ticket:
            return {
                "status": "success",
                "message": "This request was already processed.",
                "data": existing_ticket,
                "duplicate_prevented": True
            }

    ticket = {
        "ticket_id": "TKT-" + uuid.uuid4().hex[:8].upper(),
        "request_id": request_id or uuid.uuid4().hex,
        "employee_id": session_employee_id,
        "title": title.strip(),
        "description": description.strip(),
        "category": category,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    tickets.append(ticket)
    save_records("tickets.json", tickets)

    return {
        "status": "success",
        "message": "Ticket created successfully.",
        "data": ticket,
        "duplicate_prevented": False
    }


def submit_for_human_review(
    session_employee_id,
    action_type,
    action_details,
    reason
):
    """
    Add a sensitive action to the human approval queue.
    This function does not execute the requested action.
    """

    authorize_employee(session_employee_id, session_employee_id)

    review_queue = load_records("human_review.json")

    review_item = {
        "review_id": "REV-" + uuid.uuid4().hex[:8].upper(),
        "employee_id": session_employee_id,
        "action_type": action_type,
        "action_details": action_details,
        "reason": reason,
        "status": "Pending Human Approval",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    review_queue.append(review_item)
    save_records("human_review.json", review_queue)

    return {
        "status": "pending_approval",
        "message": "Your request has been sent for human review.",
        "data": review_item
    }