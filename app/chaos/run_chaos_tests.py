from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from app.chaos.failure_injector import (
    ChaosFailure,
    InjectedTaskFailure,
    InjectedTimeout,
    InjectedWorkerCrash,
    FailureInjector,
)


@dataclass
class ChaosResult:

    name: str
    status: str
    duration_seconds: float
    details: str


class ChaosTestRunner:

    def __init__(self):

        self.injector = FailureInjector()

        self.results: list[
            ChaosResult
        ] = []

    async def run_test(
        self,
        name: str,
        test_function,
    ) -> None:

        start = time.perf_counter()

        try:

            await test_function()

            status = "PASS"
            details = (
                "Expected behaviour observed."
            )

        except Exception as exc:

            status = "FAIL"

            details = (
                f"Unexpected exception: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

        duration = (
            time.perf_counter()
            - start
        )

        self.results.append(
            ChaosResult(
                name=name,
                status=status,
                duration_seconds=duration,
                details=details,
            )
        )

    async def test_task_failure(
        self,
    ) -> None:

        self.injector.enable_failure(
            failure_rate=1.0
        )

        try:

            self.injector.inject_failure()

            raise AssertionError(
                "Expected InjectedTaskFailure "
                "was not raised."
            )

        except InjectedTaskFailure:

            pass

        finally:

            self.injector.disable_failure()

    async def test_task_timeout(
        self,
    ) -> None:

        self.injector.enable_timeout(
            timeout_seconds=0.05
        )

        start = time.perf_counter()

        try:

            await asyncio.wait_for(
                self.injector.inject_timeout(),
                timeout=0.01,
            )

            raise AssertionError(
                "Expected timeout "
                "was not raised."
            )

        except asyncio.TimeoutError:

            elapsed = (
                time.perf_counter()
                - start
            )

            if elapsed > 1.0:

                raise AssertionError(
                    "Timeout recovery "
                    "took too long."
                )

        finally:

            self.injector.disable_timeout()

    async def test_worker_crash(
        self,
    ) -> None:

        self.injector.enable_worker_crash()

        try:

            self.injector.inject_worker_crash()

            raise AssertionError(
                "Expected worker crash "
                "was not raised."
            )

        except InjectedWorkerCrash:

            pass

        finally:

            self.injector.disable_worker_crash()

    async def test_recovery_after_failure(
        self,
    ) -> None:

        self.injector.enable_failure(
            failure_rate=1.0
        )

        failed = False

        try:

            self.injector.inject_failure()

        except InjectedTaskFailure:

            failed = True

        finally:

            self.injector.disable_failure()

        if not failed:

            raise AssertionError(
                "Failure was not injected."
            )

        # Recovery simulation:
        # the injector is disabled and the
        # next operation must succeed.

        self.injector.inject_failure()

    async def test_configuration_reset(
        self,
    ) -> None:

        self.injector.enable_failure(
            failure_rate=1.0
        )

        self.injector.enable_timeout(
            timeout_seconds=0.01
        )

        self.injector.enable_worker_crash()

        self.injector.disable_failure()
        self.injector.disable_timeout()
        self.injector.disable_worker_crash()

        snapshot = (
            self.injector.snapshot()
        )

        if snapshot["failure"]["enabled"]:

            raise AssertionError(
                "Failure injection remained enabled."
            )

        if snapshot["timeout"]["enabled"]:

            raise AssertionError(
                "Timeout injection remained enabled."
            )

        if snapshot["worker_crash"]["enabled"]:

            raise AssertionError(
                "Worker crash injection "
                "remained enabled."
            )

    async def run(self) -> None:

        await self.run_test(
            "task_failure_injection",
            self.test_task_failure,
        )

        await self.run_test(
            "task_timeout_injection",
            self.test_task_timeout,
        )

        await self.run_test(
            "worker_crash_simulation",
            self.test_worker_crash,
        )

        await self.run_test(
            "failure_recovery",
            self.test_recovery_after_failure,
        )

        await self.run_test(
            "chaos_configuration_reset",
            self.test_configuration_reset,
        )

    def print_report(self) -> None:

        print()
        print("=" * 70)
        print("AgentMesh Chaos Test Report")
        print("=" * 70)

        for result in self.results:

            print(
                f"{result.status:>5} | "
                f"{result.name:<32} | "
                f"{result.duration_seconds:.4f}s"
            )

            print(
                f"      {result.details}"
            )

        passed = sum(
            result.status == "PASS"
            for result in self.results
        )

        failed = sum(
            result.status == "FAIL"
            for result in self.results
        )

        print("-" * 70)

        print(
            f"Total: {len(self.results)} | "
            f"Passed: {passed} | "
            f"Failed: {failed}"
        )

        print("=" * 70)


async def main():

    runner = ChaosTestRunner()

    await runner.run()

    runner.print_report()

    if any(
        result.status == "FAIL"
        for result in runner.results
    ):

        raise SystemExit(1)


if __name__ == "__main__":

    asyncio.run(main())