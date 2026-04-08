import os
import json
import requests
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from dotenv import load_dotenv
from api.auth.oauth import get_credentials

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")
MAX_WINDOW_DAYS = 7


def extract_read_params(prompt: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are a calendar query parser. The current datetime is {now}.
Extract the time range and optional search query from the user's request.
Return ONLY this JSON object:
{{"time_min": "<ISO 8601 datetime>", "time_max": "<ISO 8601 datetime>", "search_query": "<search string or null>"}}

Rules:
- Always include timezone offset (e.g. 2026-04-07T00:00:00+00:00)
- time_max must never be more than 7 days after time_min
- If the user asks about a single day, set time_min to 00:00:00 and time_max to 23:59:59 of that day
- If no specific time is mentioned, use today as the range
- search_query is for filtering by person or keyword (e.g. "John", "standup"), set to null if not applicable
""",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "read_params",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "time_min": {"type": "string"},
                            "time_max": {"type": "string"},
                            "search_query": {"type": ["string", "null"]},
                        },
                        "required": ["time_min", "time_max", "search_query"],
                    },
                },
            },
        },
    )
    return json.loads(response.json()["choices"][0]["message"]["content"])


def enforce_max_window(time_min: str, time_max: str) -> str:
    t_min = datetime.fromisoformat(time_min)
    t_max = datetime.fromisoformat(time_max)
    if (t_max - t_min) > timedelta(days=MAX_WINDOW_DAYS):
        t_max = t_min + timedelta(days=MAX_WINDOW_DAYS)
    return t_max.isoformat()


def read(prompt: str) -> dict:
    params = extract_read_params(prompt)
    params["time_max"] = enforce_max_window(params["time_min"], params["time_max"])

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    request_kwargs = {
        "calendarId": "primary",
        "timeMin": params["time_min"],
        "timeMax": params["time_max"],
        "maxResults": 25,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if params["search_query"]:
        request_kwargs["q"] = params["search_query"]

    events_result = service.events().list(**request_kwargs).execute()

    return {
        "operation": "read",
        "time_min": params["time_min"],
        "time_max": params["time_max"],
        "events": events_result.get("items", []),
    }
