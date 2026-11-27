import asyncio

import uvicorn

from apps.api.app.main import app
from apps.api.app.core.db import init_db
from apps.api.app.services.admin_password_service import validate_admin_credentials
from apps.bot.bot_app.dispatcher import run_bot
from packages.shared.shared.config.settings import settings
from packages.shared.shared.logging.logger import setup_logging


async def run_api_server() -> None:
    config = uvicorn.Config(
        app=app,
        host=settings.web_host,
        port=settings.web_port,
        log_level=settings.log_level.lower(),
        forwarded_allow_ips=settings.web_trusted_proxies,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_all() -> None:
    setup_logging()
    validate_admin_credentials()
    await init_db()
    tasks = [
        asyncio.create_task(run_api_server(), name="web"),
        asyncio.create_task(run_bot(), name="bot"),
    ]
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            await task
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def main() -> None:
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
