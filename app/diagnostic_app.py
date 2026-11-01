import streamlit as st

st.title("Employee Assistant - Diagnostic Test")

st.write("Checkpoint 1: Streamlit is rendering.")

try:
    from app.orchestrator import process_employee_request

    st.success("Checkpoint 2: Orchestrator imported successfully.")

except Exception as error:
    st.error("Orchestrator import failed.")
    st.exception(error)

st.write("Checkpoint 3: Application reached the end of the script.")