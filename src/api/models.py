from pydantic import BaseModel as Model


class UserInput(Model):
    question: str
