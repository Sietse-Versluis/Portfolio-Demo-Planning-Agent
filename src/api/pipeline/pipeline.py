from api.pipeline.classify import classify
from api.pipeline.calendar import calendar


def pipeline(prompt: str):
    category = classify(prompt)["category"]

    if category == "calendar":
        return calendar(prompt)

    return {"message": "I can only help with calendar tasks for now."}
