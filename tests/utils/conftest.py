import structlog.testing
import pytest
from typing import Generator

from fauth.utils import Logger


@pytest.fixture
def capture_logs() -> Generator[list[dict]]:
    with structlog.testing.capture_logs() as captured:
        yield captured


@pytest.fixture
def logger() -> Logger:
    return Logger(__name__)


@pytest.fixture
def message() -> str:
    return "Test message"
