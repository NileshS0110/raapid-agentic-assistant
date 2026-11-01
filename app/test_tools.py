from app.tools import (
    get_leave_balance,
    get_reimbursement_status,
    get_asset_assignment,
    AuthorizationError
)


def run_test(test_name, test_function):

    try:
        result = test_function()
        print(f"\nPASS: {test_name}")
        print(result)

    except Exception as error:
        print(f"\nFAIL: {test_name}")
        print(type(error).__name__, "-", error)


# Test 1: Retrieve own leave balance
run_test(
    "Employee can retrieve own leave balance",
    lambda: get_leave_balance("EMP001")
)


# Test 2: Retrieve own reimbursement claims
run_test(
    "Employee can retrieve own reimbursement claims",
    lambda: get_reimbursement_status("EMP001")
)


# Test 3: Retrieve own asset assignments
run_test(
    "Employee can retrieve own assets",
    lambda: get_asset_assignment("EMP001")
)


# Test 4: Prevent access to another employee's leave balance
def unauthorized_leave_access():

    try:
        get_leave_balance(
            session_employee_id="EMP001",
            requested_employee_id="EMP002"
        )

    except AuthorizationError:
        return "Correctly blocked unauthorized access."

    raise AssertionError("Security failure: unauthorized access was allowed.")


run_test(
    "Employee cannot access another employee's leave balance",
    unauthorized_leave_access
)


# Test 5: Prevent access without authentication
def unauthenticated_access():

    try:
        get_leave_balance(
            session_employee_id=None,
            requested_employee_id="EMP001"
        )

    except AuthorizationError:
        return "Correctly blocked unauthenticated access."

    raise AssertionError("Security failure: unauthenticated access was allowed.")


run_test(
    "Unauthenticated access is blocked",
    unauthenticated_access
)