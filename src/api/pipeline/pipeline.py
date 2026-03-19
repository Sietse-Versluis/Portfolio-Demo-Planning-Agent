from api.pipeline.call_llm import call_llm


def pipeline(question: str) -> str:
    answer = call_llm(question)
    return answer
