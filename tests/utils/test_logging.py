import pytest

from fauth.utils import Logger


@pytest.mark.asyncio
async def test_info(
    capture_logs: list[dict],
    message: str,
    logger: Logger,
) -> None:
    await logger.info(message)
    assert capture_logs[0]["event"] == message
    assert capture_logs[0]["log_level"] == "info"


@pytest.mark.asyncio
async def test_debug(
    capture_logs: list[dict],
    message: str,
    logger: Logger,
) -> None:
    await logger.debug(message)
    assert capture_logs[0]["event"] == message
    assert capture_logs[0]["log_level"] == "debug"


@pytest.mark.asyncio
async def test_warning(
    capture_logs: list[dict],
    message: str,
    logger: Logger,
) -> None:
    await logger.warning(message)
    assert capture_logs[0]["event"] == message
    assert capture_logs[0]["log_level"] == "warning"


@pytest.mark.asyncio
async def test_error(
    capture_logs: list[dict],
    message: str,
    logger: Logger,
) -> None:
    await logger.error(message)
    assert capture_logs[0]["event"] == message
    assert capture_logs[0]["log_level"] == "error"
