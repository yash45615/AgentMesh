from __future__ import annotations

from typing import Any

from app.gateway.model_gateway import ModelGateway
from app.models.agent import Agent
from app.models.task import Task
from app.loadtest.config import (
    load_test_config,
)
from app.loadtest.runtime import (
    LoadTestRuntime,
)


class AgentRuntime:

    def __init__(self):

        self.model_gateway = ModelGateway()

        self.load_test_runtime = (
            LoadTestRuntime(
                execution_delay_ms=(
                    load_test_config
                    .execution_delay_ms
                )
            )
        )

    async def execute(
        self,
        agent: Agent,
        task: Task,
    ) -> dict[str, Any]:

        if load_test_config.enabled:

            return await (
                self.load_test_runtime.execute(
                    agent=agent,
                    task=task,
                )
            )

        input_data = (
            task.input_data or {}
        )

        system_prompt = (
            agent.system_prompt
            or "You are a helpful AI agent."
        )

        user_prompt = (
            f"Task type: {task.task_type}\n\n"
            f"Task input:\n{input_data}"
        )

        response = (
            await self.model_gateway.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=(
                    agent.model
                    if agent.model != "default"
                    else None
                ),
            )
        )

        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "agent_type": agent.agent_type,
            "task_id": task.id,
            "task_type": task.task_type,
            "model": response["model"],
            "content": response["content"],
            "finish_reason": (
                response["finish_reason"]
            ),
            "usage": response["usage"],
        }