from src.agents.base import BaseAgent


class WriterAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("writer")

    def run(self, content: str) -> str:
        return f"Written response:\n{content}"
