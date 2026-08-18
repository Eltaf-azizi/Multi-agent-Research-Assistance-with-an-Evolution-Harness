from src.evaluation.metrics import score_answer, summarize_scores


def evaluate_answers(answers: list[tuple[str, str]]) -> dict[str, object]:
    scores = [score_answer(answer, expected) for answer, expected in answers]
    return {"scores": scores, "summary": summarize_scores(scores)}
