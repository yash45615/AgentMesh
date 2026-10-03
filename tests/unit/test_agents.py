def test_agent_schema():

    from app.schemas.agent import AgentCreate

    agent = AgentCreate(
        name="Test Agent",
        agent_type="research",
        model="default",
        capabilities=[
            "research",
            "analysis",
        ],
        allowed_tools=[
            "web_search",
        ],
    )

    assert agent.name == "Test Agent"
    assert agent.agent_type == "research"
    assert "research" in agent.capabilities
    assert "web_search" in agent.allowed_tools


def test_agent_defaults():

    from app.schemas.agent import AgentCreate

    agent = AgentCreate(
        name="Default Agent",
    )

    assert agent.agent_type == "general"
    assert agent.model == "default"
    assert agent.max_concurrent_tasks == 5
    assert agent.timeout_seconds == 300
    assert agent.capabilities == []
    assert agent.allowed_tools == []
    assert agent.configuration == {}