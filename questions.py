import requests


API_URL = "http://127.0.0.1:8000"


def ask(question):

    try:

        response = requests.post(
            f"{API_URL}/ask",
            json={
                "question": question
            },
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        return {
            "error": "FastAPI server is not running."
        }

    except requests.exceptions.RequestException as error:

        return {
            "error": str(error)
        }


print()
print("🎓 CAMPUSCONNECT")
print("Ask anything. Type 'exit' to close.")
print()


while True:

    question = input("You: ").strip()

    if question.lower() == "exit":

        print(
            "CampusConnect: Goodbye! 👋"
        )

        break

    if not question:

        print(
            "CampusConnect: Please enter a question."
        )

        continue

    result = ask(question)

    if "error" in result:

        print(
            "CampusConnect:",
            result["error"]
        )

        continue

    answers = result.get(
        "answers",
        []
    )

    if not answers:

        print(
            "CampusConnect: No answer found."
        )

        continue

    for item in answers:

        print(
            "Answer:",
            item["answer"]
        )