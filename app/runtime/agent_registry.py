from app.models.agent import Agent


class AgentRegistry:

    def __init__(self):
        self._agents: dict[int, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.id] = agent

        print(
            f"Registered agent "
            f"{agent.id}: {agent.name}"
        )

    def get(self, agent_id: int) -> Agent | None:
        return self._agents.get(agent_id)

    def unregister(self, agent_id: int) -> None:
        self._agents.pop(agent_id, None)

    def list_agents(self) -> list[Agent]:
        return list(self._agents.values())