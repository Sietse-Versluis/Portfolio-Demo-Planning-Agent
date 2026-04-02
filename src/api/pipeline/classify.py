import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")


def classify(prompt: str) -> dict:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a classifier. Return ONLY this JSON object:
{"category": "<value>"}

Possible values: "calendar", "todo", "other"
""",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["calendar", "todo", "other"],
                            }
                        },
                        "required": ["category"],
                    },
                },
            },
        },
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])
