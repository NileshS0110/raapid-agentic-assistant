
import re


def detect_meal_limit_conflict(results):
    """
    Detect conflicting meal reimbursement limits
    in retrieved current documents.
    """

    limits_by_document = {}

    for result in results:

        metadata = result["metadata"]

        if metadata.get("status", "").lower() != "current":
            continue

        document_id = metadata.get("document_id", "")

        if document_id not in [
            "EXPENSE-2026",
            "FINANCE-FAQ-2026"
        ]:
            continue

        matches = re.findall(
            r"meal expenses?[^.]{0,150}?INR\s*([\d,]+)",
            result["text"],
            flags=re.IGNORECASE
        )

        for match in matches:
            amount = int(match.replace(",", ""))

            if document_id not in limits_by_document:
                limits_by_document[document_id] = set()

            limits_by_document[document_id].add(amount)

    policy_limits = limits_by_document.get("EXPENSE-2026", set())
    faq_limits = limits_by_document.get("FINANCE-FAQ-2026", set())

    if policy_limits and faq_limits:

        policy_limit = max(policy_limits)
        faq_limit = max(faq_limits)

        if policy_limit != faq_limit:
            return {
                "has_conflict": True,
                "message": (
                    "Conflicting meal reimbursement limits found. "
                    f"Employee Expense Policy states INR {policy_limit}, "
                    f"while Finance FAQ states INR {faq_limit}. "
                    "Please confirm with Finance before relying on either limit."
                ),
                "sources": [
                    "EXPENSE-2026",
                    "FINANCE-FAQ-2026"
                ],
                "values": {
                    "EXPENSE-2026": policy_limit,
                    "FINANCE-FAQ-2026": faq_limit
                }
            }

    return {
        "has_conflict": False,
        "message": "No conflict detected.",
        "sources": [],
        "values": {}
    }


def check_retrieval_confidence(results, threshold=0.30):
    """
    Check whether the best retrieved result meets
    the configured minimum similarity threshold.

    Threshold is provisional and must be calibrated
    using labelled evaluation queries.
    """

    if not results:
        return {
            "can_answer": False,
            "reason": "No relevant documents were retrieved."
        }

    best_score = results[0]["similarity"]

    if best_score < threshold:
        return {
            "can_answer": False,
            "reason": (
                "Retrieved document relevance is below "
                "the configured threshold."
            ),
            "best_score": best_score
        }

    return {
        "can_answer": True,
        "reason": "Retrieved document relevance passed the threshold.",
        "best_score": best_score
    }


if __name__ == "__main__":

    print("Guardrails module loaded successfully.")

    print("\nAvailable safeguards:")
    print("1. Conflicting policy detection")
    print("2. Retrieval confidence and abstention")
