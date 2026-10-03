from __future__ import annotations

from threading import Lock
from typing import Any

from app.observability.slo import slo_monitor


class Metrics:

    def __init__(self):

        self._lock = Lock()

        self._tasks_created = 0
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._tasks_retried = 0
        self._tasks_timed_out = 0

        self._llm_requests = 0
        self._llm_errors = 0

        self._total_task_latency = 0.0
        self._total_llm_latency = 0.0

        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0

        self._workers_started = 0

        self._errors: dict[str, int] = {}

    def task_created(self) -> None:

        with self._lock:

            self._tasks_created += 1

    def task_completed(
        self,
        duration: float = 0.0,
    ) -> None:

        with self._lock:

            self._tasks_completed += 1

            self._total_task_latency += (
                duration
            )

        slo_monitor.task_completed(
            latency=duration
        )

    def task_failed(self) -> None:

        with self._lock:

            self._tasks_failed += 1

        slo_monitor.task_failed()

    def task_retried(self) -> None:

        with self._lock:

            self._tasks_retried += 1

    def task_timed_out(self) -> None:

        with self._lock:

            self._tasks_timed_out += 1

        slo_monitor.task_timed_out()

    def llm_request(
        self,
        latency: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> None:

        with self._lock:

            self._llm_requests += 1

            self._total_llm_latency += (
                latency
            )

            self._prompt_tokens += (
                prompt_tokens
            )

            self._completion_tokens += (
                completion_tokens
            )

            self._total_tokens += (
                total_tokens
            )

        slo_monitor.llm_request(
            latency=latency
        )

    def worker_started_event(self) -> None:

        with self._lock:

            self._workers_started += 1

        slo_monitor.worker_started()

    def error(
        self,
        error_type: str,
    ) -> None:

        with self._lock:

            self._errors[
                error_type
            ] = (
                self._errors.get(
                    error_type,
                    0,
                )
                + 1
            )

            self._llm_errors += 1

        slo_monitor.llm_error()

    def snapshot(self) -> dict[str, Any]:

        with self._lock:

            average_task_latency = (
                self._total_task_latency
                / self._tasks_completed
                if self._tasks_completed
                else 0.0
            )

            average_llm_latency = (
                self._total_llm_latency
                / self._llm_requests
                if self._llm_requests
                else 0.0
            )

            return {
                "tasks": {
                    "created": (
                        self._tasks_created
                    ),
                    "completed": (
                        self._tasks_completed
                    ),
                    "failed": (
                        self._tasks_failed
                    ),
                    "retried": (
                        self._tasks_retried
                    ),
                    "timed_out": (
                        self._tasks_timed_out
                    ),
                    "average_latency_seconds": (
                        round(
                            average_task_latency,
                            4,
                        )
                    ),
                },
                "llm": {
                    "requests": (
                        self._llm_requests
                    ),
                    "average_latency_seconds": (
                        round(
                            average_llm_latency,
                            4,
                        )
                    ),
                    "prompt_tokens": (
                        self._prompt_tokens
                    ),
                    "completion_tokens": (
                        self._completion_tokens
                    ),
                    "total_tokens": (
                        self._total_tokens
                    ),
                },
                "workers": {
                    "started": (
                        self._workers_started
                    ),
                },
                "errors": dict(
                    self._errors
                ),
            }


metrics = Metrics()