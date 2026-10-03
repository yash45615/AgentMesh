from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_type = Column(
        String(50),
        nullable=False,
        default="general",
    )

    input_data = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    result = Column(
        JSON,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="queued",
        index=True,
    )

    priority = Column(
        Integer,
        nullable=False,
        default=5,
        index=True,
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    max_retries = Column(
        Integer,
        nullable=False,
        default=3,
    )

    timeout_seconds = Column(
        Integer,
        nullable=False,
        default=300,
    )

    worker_id = Column(
        Integer,
        ForeignKey("workers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    owner = relationship(
        "User",
        backref="tasks",
    )

    agent = relationship(
        "Agent",
        backref="tasks",
    )

    worker = relationship(
        "Worker",
        backref="tasks",
    )