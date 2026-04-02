from api.pipeline.classify import classify


def pipeline(question: str) -> str:
    answer = classify(question)
    return answer
