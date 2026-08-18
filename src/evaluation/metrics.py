from typing import Any


def score_answer(answer: str, expected: str) -> float:
    if not answer or not expected:
        return 0.0
    return 1.0 if expected.lower() in answer.lower() else 0.0


def summarize_scores(scores: list[float]) -> dict[str, Any]:
    if not scores:
        return {"average": 0.0, "count": 0}
    return {"average": sum(scores) / len(scores), "count": len(scores)}
