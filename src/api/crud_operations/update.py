import os
import json
import requests
from datetime import datetime, timedelta  # noqa: F401 — timedelta used below
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from dotenv import load_dotenv
from api.auth.oauth import get_credentials

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")


def extract_update_params(prompt: str) -> dict:
    amsterdam = ZoneInfo("Europe/Amsterdam")
    now = datetime.now(amsterdam).isoformat()
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are a calendar event update parser. The current datetime in Amsterdam (Europe/Amsterdam) is {now}.
Extract which event to update and what to change.
Return ONLY this JSON object:
{{"search_query": "<title or keyword to find the event>", "new_title": "<new title or null>", "new_start": "<ISO 8601 datetime or null>", "new_end": "<ISO 8601 datetime or null>", "new_duration_minutes": <integer or null>, "new_description": "<new description or null>", "new_location": "<new location or null>"}}

Rules:
- All times are in the Europe/Amsterdam timezone — always include the correct offset (e.g. +02:00 in summer, +01:00 in winter)
- search_query is used to find the existing event by title or keyword
- Only include fields the user wants to change — set unchanged fields to null
- If the user wants to change the duration (e.g. "make it 1.5 hours"), set new_duration_minutes and leave new_start and new_end null
- If only a new start time is given and no end time, set new_end and new_duration_minutes to null (duration will be preserved)
- Do NOT set new_start unless the user explicitly mentions a new start time
""",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "update_params",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "search_query": {"type": "string"},
                            "new_title": {"type": ["string", "null"]},
                            "new_start": {"type": ["string", "null"]},
                            "new_end": {"type": ["string", "null"]},
                            "new_duration_minutes": {"type": ["integer", "null"]},
                            "new_description": {"type": ["string", "null"]},
                            "new_location": {"type": ["string", "null"]},
                        },
                        "required": [
                            "search_query",
                            "new_title",
                            "new_start",
                            "new_end",
                            "new_duration_minutes",
                            "new_description",
                            "new_location",
                        ],
                    },
                },
            },
        },
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])


def update(prompt: str) -> dict:
    params = extract_update_params(prompt)

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
            "operation": "update",
            "error": f"Geen event gevonden voor '{params['search_query']}'",
        }

    event = events[0]
    original_start = event["start"].get("dateTime", event["start"].get("date"))
    original_end = event["end"].get("dateTime", event["end"].get("date"))

    if params["new_title"]:
        event["summary"] = params["new_title"]
    if params["new_description"]:
        event["description"] = params["new_description"]
    if params["new_location"]:
        event["location"] = params["new_location"]

    if params["new_duration_minutes"]:
        original_start_dt = datetime.fromisoformat(original_start)
        event["end"] = {"dateTime": (original_start_dt + timedelta(minutes=params["new_duration_minutes"])).isoformat()}

    if params["new_start"]:
        original_start_dt = datetime.fromisoformat(original_start)
        original_end_dt = datetime.fromisoformat(original_end)
        duration = original_end_dt - original_start_dt

        new_start_dt = datetime.fromisoformat(params["new_start"])
        event["start"] = {"dateTime": new_start_dt.isoformat()}
        event["end"] = {"dateTime": (new_start_dt + duration).isoformat()}

    if params["new_end"]:
        event["end"] = {"dateTime": params["new_end"]}

    updated_event = (
        service.events()
        .update(calendarId="primary", eventId=event["id"], body=event)
        .execute()
    )

    return {
        "operation": "update",
        "event_id": updated_event["id"],
        "title": updated_event["summary"],
        "start": updated_event["start"]["dateTime"],
        "end": updated_event["end"]["dateTime"],
        "link": updated_event.get("htmlLink"),
    }
