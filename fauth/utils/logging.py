import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.processors.KeyValueRenderer(),
    ],
    cache_logger_on_first_use=True,
)


class Logger:
    def __init__(self, name: str):
        self._logger = structlog.get_logger(name)

    async def info(self, msg: str, **kwargs):
        await self._logger.ainfo(msg, **kwargs)

    async def error(self, msg: str, **kwargs):
        await self._logger.aerror(msg, **kwargs)

    async def debug(self, msg: str, **kwargs):
        await self._logger.adebug(msg, **kwargs)

    async def warning(self, msg: str, **kwargs):
        await self._logger.awarning(msg, **kwargs)


logger = Logger("fauth")
