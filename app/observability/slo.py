from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass
class SLOTarget:
    name: str
    target: float
    direction: str
    description: str


class SLOMonitor:

    def __init__(self):

        self._lock = Lock()

        self._task_completed = 0
        self._task_failed = 0
        self._task_timed_out = 0

        self._task_latencies: list[float] = []
        self._llm_latencies: list[float] = []

        self._llm_requests = 0
        self._llm_errors = 0

        self._workers_started = 0

        self.targets = [
            SLOTarget(
                name="task_success_rate",
                target=99.0,
                direction="above",
                description=(
                    "Percentage of tasks completed "
                    "successfully."
                ),
            ),
            SLOTarget(
                name="task_failure_rate",
                target=1.0,
                direction="below",
                description=(
                    "Percentage of tasks that fail."
                ),
            ),
            SLOTarget(
                name="task_timeout_rate",
                target=1.0,
                direction="below",
                description=(
                    "Percentage of tasks that time out."
                ),
            ),
            SLOTarget(
                name="task_p95_latency_seconds",
                target=30.0,
                direction="below",
                description=(
                    "95th percentile task execution latency."
                ),
            ),
            SLOTarget(
                name="llm_p95_latency_seconds",
                target=20.0,
                direction="below",
                description=(
                    "95th percentile LLM request latency."
                ),
            ),
            SLOTarget(
                name="llm_error_rate",
                target=1.0,
                direction="below",
                description=(
                    "Percentage of LLM requests "
                    "that produce errors."
                ),
            ),
        ]

    def task_completed(
        self,
        latency: float,
    ) -> None:

        with self._lock:

            self._task_completed += 1

            self._task_latencies.append(
                float(latency)
            )

            self._trim(
                self._task_latencies
            )

    def task_failed(self) -> None:

        with self._lock:

            self._task_failed += 1

    def task_timed_out(self) -> None:

        with self._lock:

            self._task_timed_out += 1

    def llm_request(
        self,
        latency: float,
    ) -> None:

        with self._lock:

            self._llm_requests += 1

            self._llm_latencies.append(
                float(latency)
            )

            self._trim(
                self._llm_latencies
            )

    def llm_error(self) -> None:

        with self._lock:

            self._llm_errors += 1

    def worker_started(self) -> None:

        with self._lock:

            self._workers_started += 1

    @staticmethod
    def _trim(
        values: list[float],
        maximum: int = 10000,
    ) -> None:

        if len(values) > maximum:

            del values[
                :-maximum
            ]

    @staticmethod
    def _percentile(
        values: list[float],
        percentile: float,
    ) -> float:

        if not values:

            return 0.0

        ordered = sorted(values)

        index = (
            (len(ordered) - 1)
            * percentile
        )

        lower = int(index)

        upper = min(
            lower + 1,
            len(ordered) - 1,
        )

        fraction = (
            index - lower
        )

        return (
            ordered[lower]
            + (
                ordered[upper]
                - ordered[lower]
            )
            * fraction
        )

    def snapshot(self) -> dict[str, Any]:

        with self._lock:

            completed = (
                self._task_completed
            )

            failed = (
                self._task_failed
            )

            timed_out = (
                self._task_timed_out
            )

            total_tasks = (
                completed
                + failed
                + timed_out
            )

            task_success_rate = (
                (
                    completed
                    / total_tasks
                )
                * 100
                if total_tasks
                else 100.0
            )

            task_failure_rate = (
                (
                    failed
                    / total_tasks
                )
                * 100
                if total_tasks
                else 0.0
            )

            task_timeout_rate = (
                (
                    timed_out
                    / total_tasks
                )
                * 100
                if total_tasks
                else 0.0
            )

            task_p95 = (
                self._percentile(
                    self._task_latencies,
                    0.95,
                )
            )

            llm_p95 = (
                self._percentile(
                    self._llm_latencies,
                    0.95,
                )
            )

            llm_error_rate = (
                (
                    self._llm_errors
                    / self._llm_requests
                )
                * 100
                if self._llm_requests
                else 0.0
            )

            return {
                "tasks": {
                    "total": total_tasks,
                    "completed": completed,
                    "failed": failed,
                    "timed_out": timed_out,
                    "success_rate_percent": round(
                        task_success_rate,
                        2,
                    ),
                    "failure_rate_percent": round(
                        task_failure_rate,
                        2,
                    ),
                    "timeout_rate_percent": round(
                        task_timeout_rate,
                        2,
                    ),
                    "p95_latency_seconds": round(
                        task_p95,
                        4,
                    ),
                },
                "llm": {
                    "requests": (
                        self._llm_requests
                    ),
                    "errors": (
                        self._llm_errors
                    ),
                    "error_rate_percent": round(
                        llm_error_rate,
                        2,
                    ),
                    "p95_latency_seconds": round(
                        llm_p95,
                        4,
                    ),
                },
                "workers": {
                    "started": (
                        self._workers_started
                    ),
                },
            }

    def evaluate(self) -> dict[str, Any]:

        snapshot = self.snapshot()

        checks = []

        for target in self.targets:

            if target.name == (
                "task_success_rate"
            ):

                actual = (
                    snapshot["tasks"]
                    ["success_rate_percent"]
                )

            elif target.name == (
                "task_failure_rate"
            ):

                actual = (
                    snapshot["tasks"]
                    ["failure_rate_percent"]
                )

            elif target.name == (
                "task_timeout_rate"
            ):

                actual = (
                    snapshot["tasks"]
                    ["timeout_rate_percent"]
                )

            elif target.name == (
                "task_p95_latency_seconds"
            ):

                actual = (
                    snapshot["tasks"]
                    ["p95_latency_seconds"]
                )

            elif target.name == (
                "llm_p95_latency_seconds"
            ):

                actual = (
                    snapshot["llm"]
                    ["p95_latency_seconds"]
                )

            elif target.name == (
                "llm_error_rate"
            ):

                actual = (
                    snapshot["llm"]
                    ["error_rate_percent"]
                )

            else:

                continue

            if target.direction == "above":

                passed = (
                    actual >= target.target
                )

            else:

                passed = (
                    actual <= target.target
                )

            checks.append(
                {
                    "name": target.name,
                    "target": target.target,
                    "direction": target.direction,
                    "actual": actual,
                    "status": (
                        "PASS"
                        if passed
                        else "FAIL"
                    ),
                    "description": (
                        target.description
                    ),
                }
            )

        overall = all(
            check["status"] == "PASS"
            for check in checks
        )

        return {
            "overall_status": (
                "PASS"
                if overall
                else "FAIL"
            ),
            "slo_count": len(checks),
            "passed": sum(
                check["status"] == "PASS"
                for check in checks
            ),
            "failed": sum(
                check["status"] == "FAIL"
                for check in checks
            ),
            "checks": checks,
            "snapshot": snapshot,
        }


slo_monitor = SLOMonitor()