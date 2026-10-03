from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import (
    AgentCreate,
    AgentResponse,
)


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_agent(
    data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    agent = Agent(
        owner_id=current_user.id,
        name=data.name,
        description=data.description,
        agent_type=data.agent_type,
        model=data.model,
        system_prompt=data.system_prompt,
        capabilities=data.capabilities,
        allowed_tools=data.allowed_tools,
        configuration=data.configuration,
        max_concurrent_tasks=(
            data.max_concurrent_tasks
        ),
        timeout_seconds=(
            data.timeout_seconds
        ),
        is_active=True,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


@router.get(
    "",
    response_model=list[AgentResponse],
)
def list_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    statement = (
        select(Agent)
        .where(
            Agent.owner_id == current_user.id
        )
        .order_by(
            Agent.created_at.desc()
        )
    )

    return list(
        db.execute(statement)
        .scalars()
        .all()
    )


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    statement = select(Agent).where(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id,
    )

    agent = (
        db.execute(statement)
        .scalar_one_or_none()
    )

    if agent is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    return agent


@router.patch(
    "/{agent_id}",
    response_model=AgentResponse,
)
def update_agent(
    agent_id: int,
    data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    statement = select(Agent).where(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id,
    )

    agent = (
        db.execute(statement)
        .scalar_one_or_none()
    )

    if agent is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    agent.name = data.name
    agent.description = data.description
    agent.agent_type = data.agent_type
    agent.model = data.model
    agent.system_prompt = data.system_prompt
    agent.capabilities = data.capabilities
    agent.allowed_tools = data.allowed_tools
    agent.configuration = data.configuration
    agent.max_concurrent_tasks = (
        data.max_concurrent_tasks
    )
    agent.timeout_seconds = (
        data.timeout_seconds
    )

    db.commit()
    db.refresh(agent)

    return agent


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    statement = select(Agent).where(
        Agent.id == agent_id,
        Agent.owner_id == current_user.id,
    )

    agent = (
        db.execute(statement)
        .scalar_one_or_none()
    )

    if agent is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    agent.is_active = False

    db.commit()

    return None