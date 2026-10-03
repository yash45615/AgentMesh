from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):

    agent_id: int = Field(
        gt=0,
    )

    task_type: str = Field(
        default="general",
        min_length=1,
        max_length=50,
    )

    input_data: dict[str, Any] = Field(
        default_factory=dict,
    )

    priority: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
    )

    timeout_seconds: int = Field(
        default=300,
        ge=1,
        le=3600,
    )


class TaskResponse(BaseModel):

    id: int

    owner_id: int

    agent_id: int

    task_type: str

    input_data: dict[str, Any]

    result: dict[str, Any] | None

    error_message: str | None

    status: str

    priority: int

    retry_count: int

    max_retries: int

    timeout_seconds: int

    worker_id: int | None

    created_at: datetime

    started_at: datetime | None

    completed_at: datetime | None

    model_config = {
        "from_attributes": True
    }