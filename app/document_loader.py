
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"


def read_markdown_document(file_path):
    """
    Read a Markdown document and extract its metadata.
    Metadata is expected at the beginning of the file.
    """

    content = file_path.read_text(encoding="cp1252")
    lines = content.splitlines()

    metadata = {}
    body_start = 0

    # Extract metadata from the beginning of the document.
    for index, line in enumerate(lines):
        if not line.strip():
            body_start = index + 1
            break

        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    document_text = "\n".join(lines[body_start:]).strip()

    # Keep the original filename as a fallback identifier.
    metadata.setdefault("document_id", file_path.stem)
    metadata.setdefault("title", file_path.stem)
    metadata.setdefault("version", "unknown")
    metadata.setdefault("status", "unknown")
    metadata.setdefault("effective_date", "unknown")
    metadata.setdefault("owner", "unknown")

    return {
        "metadata": metadata,
        "text": document_text
    }


def create_chunks(document, chunk_size=180, overlap=30):
    """
    Split a document into word-based chunks.
    Adjacent chunks overlap to preserve context.
    """

    words = document["text"].split()

    if not words:
        return []

    chunks = []
    start = 0
    chunk_number = 1

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk_text = " ".join(words[start:end])

        chunks.append({
            "chunk_id": (
                document["metadata"]["document_id"]
                + "_"
                + str(chunk_number)
            ),
            "text": chunk_text,
            "metadata": document["metadata"].copy()
        })

        if end == len(words):
            break

        start = end - overlap
        chunk_number += 1

    return chunks


def load_knowledge_base():
    """
    Load all Markdown documents and convert them into chunks.
    """

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base folder not found: {KNOWLEDGE_BASE_DIR}"
        )

    document_files = sorted(
        KNOWLEDGE_BASE_DIR.glob("*.md")
    )

    if not document_files:
        raise FileNotFoundError(
            "No Markdown documents found in the knowledge base."
        )

    all_chunks = []

    for file_path in document_files:
        document = read_markdown_document(file_path)
        chunks = create_chunks(document)
        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":

    chunks = load_knowledge_base()

    print("\nKnowledge base loaded successfully!")
    print("Total documents:", len(list(KNOWLEDGE_BASE_DIR.glob("*.md"))))
    print("Total chunks:", len(chunks))

    print("\nDocument details:")

    seen_documents = set()

    for chunk in chunks:
        document_id = chunk["metadata"]["document_id"]

        if document_id not in seen_documents:
            seen_documents.add(document_id)

            print(
                document_id,
                "|",
                chunk["metadata"]["status"],
                "|",
                chunk["metadata"]["version"]
            )
