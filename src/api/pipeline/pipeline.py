from api.pipeline.classify import classify
from api.pipeline.calendar import classify_crud
from api.pipeline.humanize import humanize
from api.crud_operations.create import create
from api.crud_operations.read import read
from api.crud_operations.update import update
from api.crud_operations.delete import delete


def pipeline(prompt: str):
    category = classify(prompt)["category"]

    if category == "calendar":
        operation = classify_crud(prompt)

        if operation == "create":
            result = create(prompt)
        elif operation == "read":
            result = read(prompt)
        elif operation == "update":
            result = update(prompt)
        elif operation == "delete":
            result = delete(prompt)
        else:
            result = None

        if result is not None:
            return {"message": humanize(result)}

    return {"message": "I can only help with calendar tasks for now."}
