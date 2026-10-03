from app.agents.research import ResearchAgent
from app.agents.planner import PlannerAgent


AGENT_REGISTRY = {
    "research": ResearchAgent,
    "planner": PlannerAgent,
}


def get_agent(agent_type: str):

    agent_class = AGENT_REGISTRY.get(agent_type)

    if not agent_class:
        raise ValueError(
            f"Unknown agent type: {agent_type}"
        )

    return agent_class()