from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    agent_type = Column(
        String(50),
        nullable=False,
        default="general",
    )

    model = Column(
        String(100),
        nullable=False,
        default="default",
    )

    system_prompt = Column(
        Text,
        nullable=True,
    )

    capabilities = Column(
        JSON,
        nullable=False,
        default=list,
    )

    allowed_tools = Column(
        JSON,
        nullable=False,
        default=list,
    )

    configuration = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    max_concurrent_tasks = Column(
        Integer,
        nullable=False,
        default=5,
    )

    timeout_seconds = Column(
        Integer,
        nullable=False,
        default=300,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner = relationship(
        "User",
        backref="agents",
    )