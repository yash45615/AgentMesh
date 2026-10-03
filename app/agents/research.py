from app.agents.base import BaseAgent


class ResearchAgent(BaseAgent):

    name = "research"

    async def execute(self, task: dict) -> dict:

        prompt = task.get("prompt", "")

        return {
            "agent": self.name,
            "status": "completed",
            "message": f"Research task received: {prompt}",
        }