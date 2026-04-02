from fastapi import FastAPI

from api.models import Input
from api.pipeline.pipeline import pipeline

app = FastAPI()


@app.get("/api/status")
def read_status():
    return {"status": "API is online"}


@app.post("/api/agent/question")
async def ask_question(body: Input):
    return pipeline(body.question)
