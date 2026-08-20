from src.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("critic")

    def run(self, content: str) -> str:
        return f"Critique: {content}"
