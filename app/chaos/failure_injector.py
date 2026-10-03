from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


class ChaosFailure(Exception):
    """Base exception for controlled chaos failures."""


class InjectedTaskFailure(ChaosFailure):
    """Raised when a task failure is deliberately injected."""


class InjectedTimeout(ChaosFailure):
    """Raised when a deliberate timeout is injected."""


class InjectedWorkerCrash(ChaosFailure):
    """Raised when a worker crash is deliberately simulated."""


@dataclass
class ChaosConfig:
    failure_enabled: bool = False
    failure_rate: float = 0.0

    timeout_enabled: bool = False
    timeout_seconds: float = 0.0

    worker_crash_enabled: bool = False


class FailureInjector:

    def __init__(self):

        self.config = ChaosConfig()

    def enable_failure(
        self,
        failure_rate: float = 1.0,
    ) -> None:

        if not 0.0 <= failure_rate <= 1.0:

            raise ValueError(
                "failure_rate must be between "
                "0.0 and 1.0"
            )

        self.config.failure_enabled = True

        self.config.failure_rate = (
            failure_rate
        )

    def disable_failure(self) -> None:

        self.config.failure_enabled = False
        self.config.failure_rate = 0.0

    def enable_timeout(
        self,
        timeout_seconds: float,
    ) -> None:

        if timeout_seconds < 0:

            raise ValueError(
                "timeout_seconds cannot be negative"
            )

        self.config.timeout_enabled = True

        self.config.timeout_seconds = (
            timeout_seconds
        )

    def disable_timeout(self) -> None:

        self.config.timeout_enabled = False
        self.config.timeout_seconds = 0.0

    def enable_worker_crash(self) -> None:

        self.config.worker_crash_enabled = True

    def disable_worker_crash(self) -> None:

        self.config.worker_crash_enabled = False

    def should_fail(self) -> bool:

        if not self.config.failure_enabled:

            return False

        # Deterministic behaviour for
        # 100% and 0% failure rates.
        if self.config.failure_rate >= 1.0:

            return True

        if self.config.failure_rate <= 0.0:

            return False

        import random

        return (
            random.random()
            < self.config.failure_rate
        )

    def inject_failure(self) -> None:

        if self.should_fail():

            raise InjectedTaskFailure(
                "Chaos test deliberately "
                "injected a task failure."
            )

    async def inject_timeout(self) -> None:

        if not self.config.timeout_enabled:

            return

        await asyncio.sleep(
            self.config.timeout_seconds
        )

    def inject_worker_crash(self) -> None:

        if self.config.worker_crash_enabled:

            raise InjectedWorkerCrash(
                "Chaos test deliberately "
                "simulated a worker crash."
            )

    def snapshot(self) -> dict:

        return {
            "failure": {
                "enabled": (
                    self.config.failure_enabled
                ),
                "failure_rate": (
                    self.config.failure_rate
                ),
            },
            "timeout": {
                "enabled": (
                    self.config.timeout_enabled
                ),
                "timeout_seconds": (
                    self.config.timeout_seconds
                ),
            },
            "worker_crash": {
                "enabled": (
                    self.config.worker_crash_enabled
                ),
            },
        }


failure_injector = FailureInjector()