from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from datetime import datetime

from app.db.database import Base


class Worker(Base):

    __tablename__ = "workers"

    id = Column(
        Integer,
        primary_key=True,
    )

    worker_id = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    status = Column(
        String(50),
        default="healthy",
    )

    current_task_id = Column(
        Integer,
        nullable=True,
    )

    last_heartbeat = Column(
        DateTime,
        default=datetime.utcnow,
    )

    registered_at = Column(
        DateTime,
        default=datetime.utcnow,
    )