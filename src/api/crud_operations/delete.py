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


def extract_delete_params(prompt: str) -> dict:
    amsterdam = ZoneInfo("Europe/Amsterdam")
    now = datetime.now(amsterdam).isoformat()
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are a calendar event delete parser. The current datetime in Amsterdam (Europe/Amsterdam) is {now}.
Extract which event the user wants to delete.
Return ONLY this JSON object:
{{"search_query": "<core title keyword of the event>"}}

Rules:
- search_query must be the shortest meaningful keyword that identifies the event — typically 1-3 words
- Strip noise words like "appointment", "meeting", "my", "the", "tomorrow", "today", time references, and filler words
- Examples: "Delete my lunch appointment tomorrow" → "lunch", "Cancel the standup meeting on Friday" → "standup", "Remove John's birthday event" → "birthday"
""",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "delete_params",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "search_query": {"type": "string"},
                        },
                        "required": ["search_query"],
                    },
                },
            },
        },
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])


def delete(prompt: str) -> dict:
    params = extract_delete_params(prompt)

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    amsterdam = ZoneInfo("Europe/Amsterdam")
    now = datetime.now(amsterdam)
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            maxResults=5,
            singleEvents=True,
            orderBy="startTime",
            q=params["search_query"],
        )
        .execute()
    )

    events = events_result.get("items", [])
    if not events:
        return {
            "operation": "delete",
            "error": f"Geen event gevonden voor '{params['search_query']}'",
        }

    event = events[0]
    service.events().delete(calendarId="primary", eventId=event["id"]).execute()

    return {
        "operation": "delete",
        "event_id": event["id"],
        "title": event["summary"],
        "start": event["start"].get("dateTime", event["start"].get("date")),
        "end": event["end"].get("dateTime", event["end"].get("date")),
    }
