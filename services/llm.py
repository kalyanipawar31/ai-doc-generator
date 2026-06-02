import requests

def call_llm(prompt):

    incubator_endpoint = "https://eyq-incubator.america.fabric.ey.com/eyq/us/api"
    incubator_key = "kCyopezqhWQ4CXPMJJVLK3aGhI6ydBNc "
    model = "gpt-5.1"

    url = f"{incubator_endpoint}/openai/deployments/{model}/chat/completions"

    headers = {
        "api-key": incubator_key,
        "Content-Type": "application/json"
    }

    body = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            url,
            json=body,
            headers=headers,
            timeout=20
        )

        # print("STATUS:", response.status_code)
        # print("RESPONSE:", response.text)

        if response.status_code != 200:
            return None

        result = response.json()

        if "choices" not in result:
            return None

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("LLM ERROR:", str(e))
        return None