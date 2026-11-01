
import json
import requests
import numpy as np

from pathlib import Path
from app.document_loader import load_knowledge_base


# Configuration
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "all-minilm"

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_FILE = BASE_DIR / "data" / "knowledge_base_vectors.json"


def generate_embedding(text):
    """Generate an embedding using the local Ollama model."""

    payload = {
        "model": MODEL_NAME,
        "prompt": text
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()["embedding"]


def build_vector_store():
    """
    Load document chunks, generate embeddings,
    and save them locally.
    """

    print("\nLoading knowledge-base documents...")

    chunks = load_knowledge_base()

    print("Total chunks:", len(chunks))
    print("\nGenerating embeddings...")

    vector_records = []

    for index, chunk in enumerate(chunks, start=1):

        embedding = generate_embedding(chunk["text"])

        record = {
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": embedding
        }

        vector_records.append(record)

        print(
            f"Processed chunk {index}/{len(chunks)}: "
            f"{chunk['chunk_id']}"
        )

    with open(VECTOR_FILE, "w", encoding="utf-8") as file:
        json.dump(vector_records, file)

    print("\nVector store created successfully!")
    print("Total embedded chunks:", len(vector_records))
    print("Saved at:", VECTOR_FILE)

    return vector_records


def load_vector_store():
    """Load previously generated embeddings."""

    if not VECTOR_FILE.exists():
        raise FileNotFoundError(
            "Vector store not found. Run build_vector_store() first."
        )

    with open(VECTOR_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""

    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def retrieve_documents(
    question,
    top_k=3,
    include_superseded=False
):
    """
    Retrieve the most relevant document chunks.

    Current documents are used by default.
    Superseded documents are excluded deterministically.
    """

    records = load_vector_store()

    # Deterministic metadata filter.
    if not include_superseded:
        records = [
            record for record in records
            if record["metadata"].get("status", "").lower() == "current"
        ]

    if not records:
        return []

    query_embedding = generate_embedding(question)

    scored_records = []

    for record in records:

        score = cosine_similarity(
            query_embedding,
            record["embedding"]
        )

        scored_records.append({
            "chunk_id": record["chunk_id"],
            "text": record["text"],
            "metadata": record["metadata"],
            "similarity": score
        })

    scored_records.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return scored_records[:top_k]


if __name__ == "__main__":

    # Build the vector store once.
    build_vector_store()

    # Test retrieval.
    question = "How many annual paid leave days do employees get?"

    print("\nTesting retrieval for:")
    print(question)

    results = retrieve_documents(question, top_k=3)

    print("\nTop retrieved documents:")

    for result in results:
        print("\nDocument ID:", result["metadata"]["document_id"])
        print("Title:", result["metadata"]["title"])
        print("Version:", result["metadata"]["version"])
        print("Status:", result["metadata"]["status"])
        print("Similarity:", round(result["similarity"], 4))
        print("Content:", result["text"][:250])
