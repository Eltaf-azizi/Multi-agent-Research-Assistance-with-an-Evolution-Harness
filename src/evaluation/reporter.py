def format_report(summary: dict[str, object]) -> str:
    return f"Average score: {summary.get('average', 0.0)}"
