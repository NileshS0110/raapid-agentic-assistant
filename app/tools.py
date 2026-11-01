import json
from pathlib import Path


# Locate the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class ToolError(Exception):
    """Base exception for tool errors."""
    pass


class AuthorizationError(ToolError):
    """Raised when an employee attempts unauthorized access."""
    pass


class RecordNotFoundError(ToolError):
    """Raised when a requested record does not exist."""
    pass


def load_json(filename):
    """Load records from a JSON file."""

    file_path = DATA_DIR / filename

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        raise ToolError(f"Data source unavailable: {filename}")

    except json.JSONDecodeError:
        raise ToolError(f"Invalid data format in {filename}")


def authorize_employee(session_employee_id, requested_employee_id):
    """
    Allow employees to access only their own records.
    """

    if not session_employee_id:
        raise AuthorizationError("Employee authentication is required.")

    if session_employee_id != requested_employee_id:
        raise AuthorizationError(
            "Access denied. You can only access your own employee records."
        )

    employees = load_json("employees.json")

    employee = next(
        (
            emp for emp in employees
            if emp["employee_id"] == session_employee_id
            and emp["active"] is True
        ),
        None
    )

    if not employee:
        raise AuthorizationError(
            "Employee is inactive or not registered."
        )

    return employee


def get_leave_balance(session_employee_id, requested_employee_id=None):
    """Retrieve the authenticated employee's leave balance."""

    requested_employee_id = requested_employee_id or session_employee_id

    authorize_employee(session_employee_id, requested_employee_id)

    records = load_json("leave_balances.json")

    record = next(
        (
            item for item in records
            if item["employee_id"] == requested_employee_id
        ),
        None
    )

    if not record:
        raise RecordNotFoundError("Leave balance record not found.")

    return {
        "status": "success",
        "tool": "get_leave_balance",
        "data": record
    }


def get_reimbursement_status(
    session_employee_id,
    requested_employee_id=None
):
    """Retrieve the authenticated employee's reimbursement claims."""

    requested_employee_id = requested_employee_id or session_employee_id

    authorize_employee(session_employee_id, requested_employee_id)

    records = load_json("reimbursements.json")

    employee_claims = [
        item for item in records
        if item["employee_id"] == requested_employee_id
    ]

    return {
        "status": "success",
        "tool": "get_reimbursement_status",
        "data": employee_claims,
        "total_claims": len(employee_claims)
    }


def get_asset_assignment(session_employee_id, requested_employee_id=None):
    """Retrieve the authenticated employee's assigned assets."""

    requested_employee_id = requested_employee_id or session_employee_id

    authorize_employee(session_employee_id, requested_employee_id)

    records = load_json("assets.json")

    employee_assets = [
        item for item in records
        if item["employee_id"] == requested_employee_id
    ]

    return {
        "status": "success",
        "tool": "get_asset_assignment",
        "data": employee_assets,
        "total_assets": len(employee_assets)
    }