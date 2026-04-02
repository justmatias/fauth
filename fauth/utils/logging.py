from typing import Any

import structlog


class Logger:
    """Async-friendly structured logger.

    FAuth does NOT call ``structlog.configure()`` — the consumer
    owns the processor pipeline.  If the host application never
    configures structlog, the default ``dev`` renderer is used
    (coloured, human-readable output).
    """

    def __init__(self, name: str) -> None:
        self._logger = structlog.get_logger(name)

    async def info(self, msg: str, **kwargs: Any) -> None:
        await self._logger.ainfo(msg, **kwargs)

    async def error(self, msg: str, **kwargs: Any) -> None:
        await self._logger.aerror(msg, **kwargs)

    async def debug(self, msg: str, **kwargs: Any) -> None:
        await self._logger.adebug(msg, **kwargs)

    async def warning(self, msg: str, **kwargs: Any) -> None:
        await self._logger.awarning(msg, **kwargs)


logger = Logger("fauth")
