
from app.vector_store import retrieve_documents
from app.guardrails import (
    detect_meal_limit_conflict,
    check_retrieval_confidence
)


def test_meal_limit_conflict():

    question = "What is the daily meal reimbursement limit?"

    results = retrieve_documents(question, top_k=20)

    conflict = detect_meal_limit_conflict(results)

    print("\nTEST 1: Meal reimbursement conflict")
    print(conflict)

    assert conflict["has_conflict"] is True

    assert conflict["values"]["EXPENSE-2026"] == 250
    assert conflict["values"]["FINANCE-FAQ-2026"] == 300

    print("PASS: Conflicting limits correctly identified.")


def test_relevant_question():

    question = "How many annual paid leave days do employees get?"

    results = retrieve_documents(question, top_k=3)

    confidence = check_retrieval_confidence(results)

    print("\nTEST 2: Relevant policy question")
    print(confidence)

    assert confidence["can_answer"] is True

    print("PASS: Relevant question passes confidence check.")


def test_empty_retrieval_abstains():

    confidence = check_retrieval_confidence([])

    print("\nTEST 3: Empty retrieval")

    assert confidence["can_answer"] is False

    print("PASS: Assistant abstains when no documents are retrieved.")


def test_low_confidence_abstains():

    # Simulate a retrieval result below the provisional threshold.
    fake_results = [
        {
            "chunk_id": "TEST-001",
            "text": "Unrelated document content",
            "metadata": {
                "document_id": "TEST-001"
            },
            "similarity": 0.10
        }
    ]

    confidence = check_retrieval_confidence(fake_results)

    print("\nTEST 4: Low-confidence retrieval")
    print(confidence)

    assert confidence["can_answer"] is False

    print("PASS: Low-confidence retrieval triggers abstention.")


if __name__ == "__main__":

    test_meal_limit_conflict()
    test_relevant_question()
    test_empty_retrieval_abstains()
    test_low_confidence_abstains()

    print("\nAll four guardrail tests passed!")
