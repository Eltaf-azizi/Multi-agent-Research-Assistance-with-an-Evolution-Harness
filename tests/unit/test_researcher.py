from src.agents.researcher import ResearcherAgent


def test_researcher_agent_runs():
    agent = ResearcherAgent()
    result = agent.run("climate")
    assert "climate" in result
