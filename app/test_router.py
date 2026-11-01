from app.schemas import EmployeeRequest
from app.router import route_request


test_requests = [
    "What is the annual leave policy?",
    "How many leave days do I have?",
    "What is my reimbursement status?",
    "Raise a ticket for my laptop issue",
    "Hi"
]

for question in test_requests:

    request = EmployeeRequest(
        employee_id="EMP001",
        request_text=question
    )

    result = route_request(request)

    print("\nEmployee request:", question)
    print("Request type:", result.request_type.value)
    print("Route:", result.route)
    print("Reason:", result.reason)

    if result.clarification_question:
        print("Clarification:", result.clarification_question)