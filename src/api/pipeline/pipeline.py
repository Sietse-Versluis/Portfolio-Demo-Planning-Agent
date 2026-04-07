from api.pipeline.classify import classify
from api.pipeline.calendar import classify_crud
from api.crud_operations.create import create
from api.crud_operations.read import read
from api.crud_operations.update import update
from api.crud_operations.delete import delete


def pipeline(prompt: str):
    category = classify(prompt)["category"]

    if category == "calendar":
        operation = classify_crud(prompt)

        if operation == "create":
            return create(prompt)
        elif operation == "read":
            return read(prompt)
        elif operation == "update":
            return update(prompt)
        elif operation == "delete":
            return delete(prompt)

    return {"message": "I can only help with calendar tasks for now."}
