import asyncio

import uvicorn

from apps.api.app.main import app
from apps.bot.bot_app.dispatcher import run_bot
from packages.shared.shared.config.settings import settings
from packages.shared.shared.logging.logger import setup_logging


async def run_api_server() -> None:
    config = uvicorn.Config(
        app=app,
        host=settings.web_host,
        port=settings.web_port,
        log_level=settings.log_level.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_all() -> None:
    setup_logging()
    await asyncio.gather(run_api_server(), run_bot())


def main() -> None:
    asyncio.run(run_all())


if __name__ == "__main__":
    main()

