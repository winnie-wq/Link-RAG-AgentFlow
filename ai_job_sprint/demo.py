import requests

BASE_URL = "http://127.0.0.1:8000"


def ask_agent(message):

    response = requests.post(
        f"{BASE_URL}/agent",
        json={"message": message},
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":

    result = ask_agent("帮我计算 18 * 27")

    print(result)
