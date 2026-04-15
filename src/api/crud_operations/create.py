import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from dotenv import load_dotenv
from api.auth.oauth import get_credentials

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")


def extract_create_params(prompt: str) -> dict:
    amsterdam = ZoneInfo("Europe/Amsterdam")
    now = datetime.now(amsterdam).isoformat()
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are a calendar event parser. The current datetime in Amsterdam (Europe/Amsterdam) is {now}.
Extract the event details from the user's request.
Return ONLY this JSON object:
{{"title": "<event title>", "start": "<ISO 8601 datetime>", "end": "<ISO 8601 datetime>", "description": "<description or null>", "location": "<location or null>"}}

Rules:
- All times are in the Europe/Amsterdam timezone — always include the correct offset (e.g. +02:00 in summer, +01:00 in winter)
- If the user says "10am", that means 10:00 Amsterdam time, so the result must be e.g. 2026-04-15T10:00:00+02:00
- If no end time is given, assume 1 hour after start
- If no date is mentioned, assume today
- title must be a short descriptive name for the event
- description and location are optional, set to null if not mentioned
""",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "create_params",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "start": {"type": "string"},
                            "end": {"type": "string"},
                            "description": {"type": ["string", "null"]},
                            "location": {"type": ["string", "null"]},
                        },
                        "required": [
                            "title",
                            "start",
                            "end",
                            "description",
                            "location",
                        ],
                    },
                },
            },
        },
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])


def create(prompt: str) -> dict:
    params = extract_create_params(prompt)

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    event_body = {
        "summary": params["title"],
        "start": {"dateTime": params["start"]},
        "end": {"dateTime": params["end"]},
    }
    if params["description"]:
        event_body["description"] = params["description"]
    if params["location"]:
        event_body["location"] = params["location"]

    created_event = (
        service.events().insert(calendarId="primary", body=event_body).execute()
    )

    return {
        "operation": "create",
        "event_id": created_event["id"],
        "title": created_event["summary"],
        "start": created_event["start"]["dateTime"],
        "end": created_event["end"]["dateTime"],
        "link": created_event.get("htmlLink"),
    }
