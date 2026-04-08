import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from api.models import Input
from api.pipeline.pipeline import pipeline
from api.auth.oauth import build_flow, TOKEN_FILE

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = FastAPI()

_flows: dict = {}


@app.get("/api/status")
def read_status():
    return {"status": "API is online"}


@app.post("/api/agent/question")
async def ask_question(body: Input):
    return pipeline(body.question)


@app.get("/auth/login")
def login():
    flow = build_flow()
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
    _flows[state] = flow
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
def callback(request: Request, state: str):
    flow = _flows.pop(state, None)
    if flow is None:
        raise HTTPException(status_code=400, detail="Ongeldige OAuth state")
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    with open(TOKEN_FILE, "w") as token_file:
        token_file.write(creds.to_json())

    return {"message": "Succesvol geauthenticeerd!"}
