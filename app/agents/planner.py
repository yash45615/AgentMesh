from app.agents.base import BaseAgent


class PlannerAgent(BaseAgent):

    name = "planner"

    async def execute(self, task: dict) -> dict:

        objective = task.get("objective", "")

        return {
            "agent": self.name,
            "status": "completed",
            "objective": objective,
            "plan": [
                "Analyze objective",
                "Break objective into subtasks",
                "Execute subtasks",
                "Validate result",
            ],
        }