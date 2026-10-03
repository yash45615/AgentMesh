from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


def create_agent(
    db: Session,
    owner_id: int,
    data: AgentCreate,
) -> Agent:

    agent = Agent(
        owner_id=owner_id,
        name=data.name,
        description=data.description,
        agent_type=data.agent_type,
        model=data.model,
        system_prompt=data.system_prompt,
        capabilities=data.capabilities,
        allowed_tools=data.allowed_tools,
        configuration=data.configuration,
        max_concurrent_tasks=data.max_concurrent_tasks,
        timeout_seconds=data.timeout_seconds,
        is_active=True,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


def get_agent(
    db: Session,
    agent_id: int,
    owner_id: int,
) -> Agent | None:

    statement = select(Agent).where(
        Agent.id == agent_id,
        Agent.owner_id == owner_id,
    )

    return db.execute(statement).scalar_one_or_none()


def get_agents(
    db: Session,
    owner_id: int,
) -> list[Agent]:

    statement = (
        select(Agent)
        .where(Agent.owner_id == owner_id)
        .order_by(Agent.created_at.desc())
    )

    return list(
        db.execute(statement).scalars().all()
    )


def update_agent(
    db: Session,
    agent: Agent,
    data: AgentUpdate,
) -> Agent:

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    return agent


def delete_agent(
    db: Session,
    agent: Agent,
) -> None:

    db.delete(agent)
    db.commit()