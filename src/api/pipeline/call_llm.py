import os

import requests
from dotenv import load_dotenv

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")


def call_llm(question: str) -> str:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {"role": "system", "content": "Je bent een behulpzame assistent."},
                {"role": "user", "content": question},
            ],
        },
    )
    return response.json()["choices"][0]["message"]["content"].strip()
