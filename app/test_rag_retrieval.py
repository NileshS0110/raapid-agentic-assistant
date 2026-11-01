
from app.vector_store import retrieve_documents


def test_current_leave_policy_retrieved():
    """The current 2026 leave policy should be retrieved."""

    question = "How many annual paid leave days do employees get?"

    results = retrieve_documents(question, top_k=3)

    document_ids = [
        result["metadata"]["document_id"]
        for result in results
    ]

    print("\nCurrent leave policy results:", document_ids)

    assert "LEAVE-2026" in document_ids, (
        "Current 2026 leave policy was not retrieved."
    )

    print("PASS: Current leave policy retrieved.")


def test_superseded_policy_excluded():
    """Superseded documents must not appear in current-policy retrieval."""

    question = "How many annual paid leave days do employees get?"

    # Retrieve all eligible current chunks to check the filter.
    results = retrieve_documents(question, top_k=20)

    document_ids = [
        result["metadata"]["document_id"]
        for result in results
    ]

    print("\nSuperseded policy test results:", document_ids)

    assert "LEAVE-2024" not in document_ids, (
        "ERROR: Superseded 2024 policy was retrieved."
    )

    assert "LEAVE-2026" in document_ids, (
        "ERROR: Current 2026 policy was not retrieved."
    )

    print("PASS: Superseded policy excluded.")


def test_conflicting_sources_retrieved():
    """Both current sources containing conflicting meal limits
    should be available to the conflict-detection stage.
    """

    question = "What is the daily meal reimbursement limit?"

    results = retrieve_documents(question, top_k=20)

    document_ids = [
        result["metadata"]["document_id"]
        for result in results
    ]

    print("\nMeal reimbursement results:", document_ids)

    assert "EXPENSE-2026" in document_ids, (
        "Expense policy was not retrieved."
    )

    assert "FINANCE-FAQ-2026" in document_ids, (
        "Finance FAQ was not retrieved."
    )

    print("PASS: Both conflicting sources retrieved.")


if __name__ == "__main__":

    test_current_leave_policy_retrieved()
    test_superseded_policy_excluded()
    test_conflicting_sources_retrieved()

    print("\nAll three retrieval tests passed!")
