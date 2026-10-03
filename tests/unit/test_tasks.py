def test_task_schema():

    from app.schemas.task import TaskCreate

    task = TaskCreate(
        agent_id=1,
        task_type="research",
        input_data={
            "query": "test"
        },
        priority=8,
        max_retries=3,
        timeout_seconds=120,
    )

    assert task.agent_id == 1
    assert task.task_type == "research"
    assert task.priority == 8
    assert task.max_retries == 3
    assert task.timeout_seconds == 120


def test_task_defaults():

    from app.schemas.task import TaskCreate

    task = TaskCreate(
        agent_id=1
    )

    assert task.task_type == "general"
    assert task.input_data == {}
    assert task.priority == 5
    assert task.max_retries == 3
    assert task.timeout_seconds == 300