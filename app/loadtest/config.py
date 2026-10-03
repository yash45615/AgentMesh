from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class LoadTestConfig:

    enabled: bool = False

    execution_delay_ms: int = 20

    task_count: int = 100

    concurrency: int = 10

    benchmark_name: str = "agentmesh-load-test"

    @classmethod
    def from_environment(
        cls,
    ) -> "LoadTestConfig":

        return cls(
            enabled=(
                os.getenv(
                    "AGENTMESH_LOAD_TEST",
                    "false",
                ).lower()
                == "true"
            ),
            execution_delay_ms=int(
                os.getenv(
                    "AGENTMESH_LOAD_TEST_DELAY_MS",
                    "20",
                )
            ),
            task_count=int(
                os.getenv(
                    "AGENTMESH_LOAD_TEST_TASKS",
                    "100",
                )
            ),
            concurrency=int(
                os.getenv(
                    "AGENTMESH_LOAD_TEST_CONCURRENCY",
                    "10",
                )
            ),
            benchmark_name=os.getenv(
                "AGENTMESH_BENCHMARK_NAME",
                "agentmesh-load-test",
            ),
        )


load_test_config = (
    LoadTestConfig.from_environment()
)