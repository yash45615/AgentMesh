from abc import ABC, abstractmethod


class BaseAgent(ABC):

    name: str = "base"

    @abstractmethod
    async def execute(self, task: dict) -> dict:
        """
        Execute an agent task.
        """

        raise NotImplementedError