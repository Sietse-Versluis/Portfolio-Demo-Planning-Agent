import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")


def classify_crud(prompt: str) -> str:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a classifier. Return ONLY this JSON object:
{"operation": "<value>"}

Possible values:
- "create": adding, planning, scheduling, or creating a new event, meeting, appointment, or deadline
- "read": asking about, listing, checking, or retrieving existing events or the agenda
- "update": changing, editing, rescheduling, moving, or modifying details of an existing event (e.g. time, location, attendees, frequency) — the event still exists afterwards
- "delete": permanently removing an event from the calendar — use this when the user says cancel, remove, delete, clear, or drop. If the event will no longer exist afterwards, it is always delete, never update
""",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "crud_classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["create", "read", "update", "delete"],
                            }
                        },
                        "required": ["operation"],
                    },
                },
            },
        },
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])["operation"]
