from src.agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("researcher")

    def run(self, query: str) -> str:
        return f"Research result for: {query}"
