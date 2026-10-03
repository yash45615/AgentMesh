import asyncio

import pytest

from app.chaos.failure_injector import (
    FailureInjector,
    InjectedTaskFailure,
    InjectedWorkerCrash,
)


def test_failure_injection():

    injector = FailureInjector()

    injector.enable_failure(
        failure_rate=1.0
    )

    with pytest.raises(
        InjectedTaskFailure
    ):

        injector.inject_failure()


def test_failure_disabled():

    injector = FailureInjector()

    injector.disable_failure()

    injector.inject_failure()


def test_worker_crash_injection():

    injector = FailureInjector()

    injector.enable_worker_crash()

    with pytest.raises(
        InjectedWorkerCrash
    ):

        injector.inject_worker_crash()


def test_worker_crash_disabled():

    injector = FailureInjector()

    injector.disable_worker_crash()

    injector.inject_worker_crash()


def test_configuration_reset():

    injector = FailureInjector()

    injector.enable_failure(
        failure_rate=1.0
    )

    injector.enable_timeout(
        timeout_seconds=1
    )

    injector.enable_worker_crash()

    injector.disable_failure()
    injector.disable_timeout()
    injector.disable_worker_crash()

    snapshot = injector.snapshot()

    assert (
        snapshot["failure"]["enabled"]
        is False
    )

    assert (
        snapshot["timeout"]["enabled"]
        is False
    )

    assert (
        snapshot["worker_crash"]["enabled"]
        is False
    )


@pytest.mark.asyncio
async def test_timeout_injection():

    injector = FailureInjector()

    injector.enable_timeout(
        timeout_seconds=0.1
    )

    with pytest.raises(
        asyncio.TimeoutError
    ):

        await asyncio.wait_for(
            injector.inject_timeout(),
            timeout=0.01,
        )