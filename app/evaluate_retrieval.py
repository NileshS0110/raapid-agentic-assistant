import json
from pathlib import Path
from app.vector_store import retrieve_documents

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_FILE = BASE_DIR / "evals" / "retrieval_evaluation.json"


def evaluate_retrieval():
    with open(EVAL_FILE, "r", encoding="utf-8-sig") as file:
        evaluation_data = json.load(file)

    queries = evaluation_data["queries"]
    k = evaluation_data.get("retrieval_k", 3)

    total_precision = 0
    total_recall = 0
    total_hit_rate = 0
    results = []

    print("\n" + "=" * 75)
    print("RETRIEVAL QUALITY EVALUATION")
    print("=" * 75)
    print(f"Total queries: {len(queries)}")
    print(f"Documents retrieved per query (K): {k}")

    for item in queries:
        query_id = item["id"]
        question = item["query"]
        expected = set(item["expected_documents"])

        print(f"\nRunning {query_id}: {question}")

        retrieved_results = retrieve_documents(
            question,
            top_k=k,
            include_superseded=False
        )

        retrieved = [
            result["metadata"]["document_id"]
            for result in retrieved_results
        ]

        retrieved_set = set(retrieved)
        relevant_found = expected.intersection(retrieved_set)

        precision = len(relevant_found) / k if k else 0
        recall = len(relevant_found) / len(expected) if expected else 0
        hit_rate = 1 if relevant_found else 0

        total_precision += precision
        total_recall += recall
        total_hit_rate += hit_rate

        result = {
            "id": query_id,
            "query": question,
            "expected_documents": sorted(expected),
            "retrieved_documents": retrieved,
            "relevant_documents_found": sorted(relevant_found),
            "precision_at_k": round(precision, 4),
            "recall_at_k": round(recall, 4),
            "hit": bool(hit_rate)
        }

        results.append(result)

        print(f"Expected documents: {sorted(expected)}")
        print(f"Retrieved documents: {retrieved}")
        print(f"Relevant documents found: {sorted(relevant_found)}")
        print(f"Precision@{k}: {precision:.2%}")
        print(f"Recall@{k}: {recall:.2%}")
        print(f"Hit: {'YES' if hit_rate else 'NO'}")

    count = len(queries)

    average_precision = total_precision / count if count else 0
    average_recall = total_recall / count if count else 0
    average_hit_rate = total_hit_rate / count if count else 0

    summary = {
        "total_queries": count,
        "retrieval_k": k,
        "average_precision_at_k": round(average_precision, 4),
        "average_recall_at_k": round(average_recall, 4),
        "hit_rate": round(average_hit_rate, 4),
        "query_results": results
    }

    output_file = BASE_DIR / "evals" / "retrieval_results.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 75)
    print("OVERALL RETRIEVAL EVALUATION SUMMARY")
    print("=" * 75)
    print(f"Queries evaluated: {count}")
    print(f"Average Precision@{k}: {average_precision:.2%}")
    print(f"Average Recall@{k}: {average_recall:.2%}")
    print(f"Hit Rate: {average_hit_rate:.2%}")
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    evaluate_retrieval()