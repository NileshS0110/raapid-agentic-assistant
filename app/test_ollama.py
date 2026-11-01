import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"


def ask_qwen(question):
    """Send a question to Qwen through the local Ollama API."""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful internal company assistant. Give clear, concise and factual answers."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()
        return result["message"]["content"]

    except requests.exceptions.Timeout:
        return "Error: The model took too long to respond."

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Check whether Ollama is running."

    except requests.exceptions.RequestException as error:
        return f"Error communicating with Ollama: {error}"


if __name__ == "__main__":
    question = "What is an employee leave policy? Explain in two sentences."

    print("\nSending question to Qwen...\n")

    answer = ask_qwen(question)

    print("Qwen response:")
    print(answer)