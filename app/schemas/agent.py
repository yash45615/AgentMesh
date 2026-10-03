from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    agent_type: str = "general"

    model: str = "default"

    system_prompt: str | None = None

    capabilities: list[str] = Field(
        default_factory=list
    )

    allowed_tools: list[str] = Field(
        default_factory=list
    )

    configuration: dict[str, Any] = Field(
        default_factory=dict
    )

    max_concurrent_tasks: int = Field(
        default=5,
        ge=1,
        le=100,
    )

    timeout_seconds: int = Field(
        default=300,
        ge=1,
        le=3600,
    )


class AgentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    agent_type: str | None = None

    model: str | None = None

    system_prompt: str | None = None

    capabilities: list[str] | None = None

    allowed_tools: list[str] | None = None

    configuration: dict[str, Any] | None = None

    max_concurrent_tasks: int | None = Field(
        default=None,
        ge=1,
        le=100,
    )

    timeout_seconds: int | None = Field(
        default=None,
        ge=1,
        le=3600,
    )

    is_active: bool | None = None


class AgentResponse(BaseModel):
    id: int
    owner_id: int

    name: str
    description: str | None

    agent_type: str
    model: str

    system_prompt: str | None

    capabilities: list[str]
    allowed_tools: list[str]

    configuration: dict[str, Any]

    max_concurrent_tasks: int
    timeout_seconds: int

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }