import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")


def humanize(result: dict) -> str:
    response = requests.post(
        LM_STUDIO_URL,
        json={
            "model": "local-model",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a helpful assistant that turns calendar operation results into short, friendly responses.
Keep it to 1-2 sentences. Be direct and clear. Do not wrap event titles or any words in quotes.

If the result contains an "error" key, acknowledge that the action failed and explain why in plain language.

Examples:
- delete success → "Done! I've deleted 'Eat Lunch' on June 4th."
- create success → "Scheduled! 'Team standup' is on your calendar for Monday at 10:00."
- update success → "Updated! 'Weekly sync' has been moved to Thursday at 14:00."
- read with events → summarize the events found in a short sentence or two
- read with no events → "No events found in that time range."
- error → "I couldn't find an event matching that description. Could you be more specific?"
""",
                },
                {"role": "user", "content": json.dumps(result)},
            ],
        },
    )
    return response.json()["choices"][0]["message"]["content"].strip()
