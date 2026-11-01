
import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "all-minilm"


def generate_embedding(text):
    payload = {
        "model": MODEL_NAME,
        "prompt": text
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        return result["embedding"]

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Ollama.")
        print("Please check whether Ollama is running.")
        return None

    except requests.exceptions.Timeout:
        print("ERROR: Embedding request timed out.")
        return None

    except requests.exceptions.RequestException as error:
        print("ERROR:", error)
        return None


if __name__ == "__main__":

    sample_text = (
        "Employees are entitled to 20 days "
        "of annual paid leave per calendar year."
    )

    print("\nTesting Ollama embedding model...")
    print("Model:", MODEL_NAME)

    embedding = generate_embedding(sample_text)

    if embedding is not None:
        print("\nSUCCESS! Embedding generated.")
        print("Number of dimensions:", len(embedding))
        print("First 10 values:", embedding[:10])
