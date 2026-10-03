"""
Central SQLAlchemy model registry.

Import every ORM model here so SQLAlchemy knows about all
relationship targets before any query is executed.
"""

from app.models.user import User
from app.models.agent import Agent
from app.models.worker import Worker
from app.models.task import Task

__all__ = [
    "User",
    "Agent",
    "Worker",
    "Task",
]