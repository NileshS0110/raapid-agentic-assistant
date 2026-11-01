
import streamlit as st

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Employee AI Assistant",
    page_icon="",
    layout="wide"
)

# --------------------------------------------------
# 2. IMPORT ORCHESTRATOR
# --------------------------------------------------

try:
    from app.orchestrator import (
        process_employee_request,
        SESSION_EMPLOYEE_ID
    )

    ORCHESTRATOR_READY = True
    IMPORT_ERROR = None

except Exception as error:

    ORCHESTRATOR_READY = False
    IMPORT_ERROR = error
    SESSION_EMPLOYEE_ID = "Unavailable"


# --------------------------------------------------
# 3. PAGE HEADER
# --------------------------------------------------

st.title("Employee AI Assistant")

st.caption(
    "Your AI-powered assistant for company policies, "
    "employee records and service requests."
)

if not ORCHESTRATOR_READY:

    st.error("The assistant could not be initialized.")
    st.exception(IMPORT_ERROR)
    st.stop()


# --------------------------------------------------
# 4. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("Employee Session")

    st.write("Employee ID:", SESSION_EMPLOYEE_ID)
    st.write("Authentication: Demo session")

    st.divider()

    st.subheader("Available Services")

    st.markdown("""
    - Company policy questions
    - Leave balance enquiries
    - Reimbursement status
    - Assigned asset lookup
    - IT ticket creation
    - Human approval workflows
    """)

    st.divider()

    if st.button("Clear Conversation"):

        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# 5. INITIALIZE CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------------------------
# 6. WELCOME MESSAGE
# --------------------------------------------------

if not st.session_state.messages:

    st.info(
        "Welcome! I can help you with company policies, "
        "employee records and service requests."
    )

    st.subheader("Try asking")

    examples = [
        "How many annual paid leave days do employees get?",
        "How many leave days do I have?",
        "What is my reimbursement status?",
        "Show me my assigned assets.",
        "Raise a ticket for my laptop issue.",
        "Update my bank details."
    ]

    for example in examples:

        st.markdown(f"- {example}")


# --------------------------------------------------
# 7. DISPLAY CONVERSATION HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("response"):

            with st.expander("View Structured Response"):

                st.json(message["response"])


# --------------------------------------------------
# 8. FORMAT ASSISTANT RESPONSE
# --------------------------------------------------

def format_response(response):

    """
    Convert structured orchestrator output into
    a conversational response for the employee.
    """

    status = response.get("status")
    request_type = response.get("request_type")
    details = response.get("details")

    # ----------------------------------------------
    # Policy questions
    # ----------------------------------------------

    if request_type == "policy_question":

        return response.get(
            "message",
            "I could not generate a policy response."
        )

    # ----------------------------------------------
    # Employee record queries
    # ----------------------------------------------

    if request_type == "record_query":

        if status != "success":

            return response.get(
                "message",
                "I could not retrieve your employee record."
            )

        # Leave balance.
        if (
            isinstance(details, dict)
            and "annual_leave_remaining" in details
        ):

            return (
                f"You have **{details['annual_leave_remaining']} "
                f"days of annual leave remaining**.\n\n"
                f"- Total annual leave entitlement: "
                f"{details['annual_leave_total']} days\n"
                f"- Annual leave used: "
                f"{details['annual_leave_used']} days\n"
                f"- Sick leave remaining: "
                f"{details['sick_leave_remaining']} days"
            )

        # Reimbursement claims.
        if isinstance(details, list):

            if not details:

                return "You currently have no records for this request."

            if "claim_id" in details[0]:

                output = [
                    "Here is the status of your reimbursement claims:"
                ]

                for item in details:

                    output.append(
                        f"\n**{item['claim_id']}**\n"
                        f"- Amount: ₹{item['amount']}\n"
                        f"- Category: {item['category']}\n"
                        f"- Status: {item['status']}\n"
                        f"- Submitted: {item['submission_date']}"
                    )

                return "\n\n".join(output)

            # Assigned assets.
            if "asset_id" in details[0]:

                output = ["Here are your currently assigned assets:"]

                for item in details:

                    output.append(
                        f"\n**{item['asset_type']}**\n"
                        f"- Brand: {item['brand']}\n"
                        f"- Model: {item['model']}\n"
                        f"- Status: {item['status']}"
                    )

                return "\n\n".join(output)

        return response.get(
            "message",
            "Your employee record was retrieved."
        )

    # ----------------------------------------------
    # Action requests
    # ----------------------------------------------

    if request_type == "action_request":

        if status == "success" and isinstance(details, dict):

            ticket_id = details.get("ticket_id")

            if ticket_id:

                return (
                    f"Your ticket has been created successfully.\n\n"
                    f"**Ticket ID:** {ticket_id}\n\n"
                    f"- Title: {details.get('title')}\n"
                    f"- Category: {details.get('category')}\n"
                    f"- Priority: {details.get('priority')}\n"
                    f"- Status: {details.get('status')}"
                )

        if status == "pending_approval":

            return (
                "Your request has been submitted for human review.\n\n"
                "**It has not been executed automatically.** "
                "A designated reviewer must verify and approve it."
            )

        return response.get(
            "message",
            "Your action could not be completed."
        )

    # ----------------------------------------------
    # Clarification and other statuses
    # ----------------------------------------------

    return response.get(
        "message",
        "I could not process your request."
    )


# --------------------------------------------------
# 9. DISPLAY CITATIONS
# --------------------------------------------------

def display_citations(citations):

    if not citations:
        return

    st.markdown("**Sources used:**")

    for citation in citations:

        if isinstance(citation, dict):

            document_id = citation.get(
                "document_id",
                "Unknown"
            )

            version = citation.get("version", "")

            effective_date = citation.get(
                "effective_date",
                ""
            )

            st.markdown(
                f"- **{document_id}**"
                f" | Version: {version}"
                f" | Effective: {effective_date}"
            )


# --------------------------------------------------
# 10. CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask about policies, leave, reimbursements or services..."
)


if question:

    # Save employee message.
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    # Process employee request.
    with st.chat_message("assistant"):

        try:

            with st.spinner("Processing your request..."):

                response = process_employee_request(question)

            # Conversational response.
            formatted_message = format_response(response)

            st.markdown(formatted_message)

            # Status.
            status = response.get("status", "unknown")

            st.caption(f"Request status: {status}")

            # Clarification.
            clarification = response.get(
                "clarification_question"
            )

            if clarification:

                st.info(clarification)

            # Human review.
            if response.get("requires_human_review"):

                st.warning(
                    "Human approval is required. "
                    "The requested action has not been executed."
                )

            # Citations.
            display_citations(
                response.get("citations", [])
            )

            # Tool calls.
            tool_calls = response.get("tool_calls", [])

            if tool_calls:

                with st.expander("Tools executed"):

                    st.json(tool_calls)

            # Full structured output.
            with st.expander("View Structured Response"):

                st.json(response)

            # Save assistant response.
            st.session_state.messages.append({

                "role": "assistant",

                "content": formatted_message,

                "response": response

            })

        except Exception as error:

            st.error(
                "Something went wrong while processing your request."
            )

            st.exception(error)
