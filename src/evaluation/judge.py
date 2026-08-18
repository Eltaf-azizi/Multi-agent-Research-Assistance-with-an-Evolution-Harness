def judge_answer(answer: str, expected: str) -> str:
    return "pass" if expected.lower() in answer.lower() else "fail"
