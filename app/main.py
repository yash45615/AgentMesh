from fastapi import FastAPI

from app.api.routes import (
    auth,
    user,
    agents,
    task,
    health,
    slo,
)

from app.observability.logging import (
    configure_logging,
)


configure_logging()


app = FastAPI(
    title="AgentMesh",
    description=(
        "Distributed AI Agent "
        "Runtime & Execution Platform"
    ),
    version="0.5.0",
)


app.include_router(
    auth.router
)

app.include_router(
    user.router
)

app.include_router(
    agents.router
)

app.include_router(
    task.router
)

app.include_router(
    health.router
)

app.include_router(
    slo.router
)