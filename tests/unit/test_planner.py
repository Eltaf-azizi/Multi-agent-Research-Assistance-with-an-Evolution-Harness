from src.agents.planner import PlannerAgent


def test_planner_agent_runs():
    agent = PlannerAgent()
    result = agent.run("AI safety")
    assert "AI safety" in result
