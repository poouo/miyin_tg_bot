import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError

from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.handlers.commands import router as command_router
from apps.bot.bot_app.handlers.group_events import router as group_router
from apps.bot.bot_app.tasks import kick_unverified_task, recover_mute_task

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(command_router)
    dp.include_router(group_router)
    return dp


async def run_bot() -> None:
    runtime = await get_runtime_config()
    token = runtime.telegram_bot_token.strip()
    if not token or token == "replace_me":
        logger.warning("TELEGRAM_BOT_TOKEN is not configured; bot polling is disabled.")
        return

    try:
        bot = Bot(token=token)
    except TokenValidationError:
        logger.error("TELEGRAM_BOT_TOKEN is invalid; bot polling is disabled.")
        return

    dp = build_dispatcher()

    recover_task = asyncio.create_task(recover_mute_task(bot))
    kick_task = asyncio.create_task(kick_unverified_task(bot))
    try:
        await dp.start_polling(bot)
    except Exception as exc:
        logger.exception("Bot polling crashed and was stopped: %s", exc)
    finally:
        recover_task.cancel()
        kick_task.cancel()
        await bot.session.close()
