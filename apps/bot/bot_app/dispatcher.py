import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, BotCommandScopeDefault
from aiogram.utils.token import TokenValidationError, validate_token

from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.bot.bot_app.handlers.commands import router as command_router
from apps.bot.bot_app.handlers.group_events import router as group_router
from apps.bot.bot_app.tasks import kick_unverified_task, recover_mute_task

logger = logging.getLogger(__name__)


USER_COMMANDS = [
    BotCommand(command="help", description="Show commands"),
    BotCommand(command="ping", description="Check bot status"),
    BotCommand(command="ask", description="Ask AI"),
    BotCommand(command="verify", description="Complete join verification"),
]

ADMIN_COMMANDS = [
    *USER_COMMANDS,
    BotCommand(command="ban", description="Ban a user"),
    BotCommand(command="unban", description="Unban a user"),
    BotCommand(command="kick", description="Remove a user and delay rejoin"),
    BotCommand(command="mute", description="Mute a user"),
    BotCommand(command="unmute", description="Unmute a user"),
]


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeAllChatAdministrators())


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(command_router)
    dp.include_router(group_router)
    return dp


class BotSupervisor:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._reload_event = asyncio.Event()
        self._polling_task: asyncio.Task | None = None
        self._running_token: str = ""
        self._invalid_token: str = ""
        self._missing_token_logged: bool = False

    async def notify_reload(self, reason: str = "manual") -> None:
        logger.info("Bot runtime reload requested: %s", reason)
        self._reload_event.set()

    async def run_forever(self) -> None:
        self._reload_event.set()
        while True:
            try:
                await asyncio.wait_for(self._reload_event.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                pass

            self._reload_event.clear()
            async with self._lock:
                await self._sync_with_runtime()
                await self._check_polling_health()

    async def _sync_with_runtime(self) -> None:
        runtime = await get_runtime_config()
        token = runtime.telegram_bot_token.strip()

        if not token or token == "replace_me":
            await self._stop_polling("token_missing")
            if not self._missing_token_logged:
                logger.warning("TELEGRAM_BOT_TOKEN is not configured; bot polling is disabled.")
            self._missing_token_logged = True
            self._invalid_token = ""
            return

        self._missing_token_logged = False

        if self._polling_task and not self._polling_task.done() and token == self._running_token:
            return

        if not self._polling_task and token == self._invalid_token:
            return

        try:
            validate_token(token)
        except TokenValidationError:
            if token != self._invalid_token:
                logger.error("TELEGRAM_BOT_TOKEN is invalid; bot polling is disabled.")
            self._invalid_token = token
            await self._stop_polling("token_invalid")
            return

        self._invalid_token = ""
        await self._stop_polling("token_changed")
        self._running_token = token
        self._polling_task = asyncio.create_task(self._polling_loop(token), name="tg-bot-polling")
        logger.info("Bot polling started.")

    async def _check_polling_health(self) -> None:
        if self._polling_task is None:
            return
        if not self._polling_task.done():
            return

        task = self._polling_task
        self._polling_task = None
        self._running_token = ""
        with suppress(asyncio.CancelledError):
            exc = task.exception()
            if exc:
                logger.error("Bot polling stopped unexpectedly: %s", exc)
            else:
                logger.warning("Bot polling task exited.")
        self._reload_event.set()

    async def _stop_polling(self, reason: str) -> None:
        task = self._polling_task
        self._polling_task = None
        self._running_token = ""
        if task is None:
            return
        logger.info("Stopping bot polling: %s", reason)
        task.cancel()
        with suppress(asyncio.CancelledError, Exception):
            await task

    async def _polling_loop(self, token: str) -> None:
        bot = Bot(token=token)
        dp = build_dispatcher()
        recover_task = asyncio.create_task(recover_mute_task(bot), name="recover-mute-task")
        kick_task = asyncio.create_task(kick_unverified_task(bot), name="kick-unverified-task")
        try:
            await setup_bot_commands(bot)
            await dp.start_polling(bot)
        finally:
            recover_task.cancel()
            kick_task.cancel()
            with suppress(asyncio.CancelledError):
                await recover_task
            with suppress(asyncio.CancelledError):
                await kick_task
            await bot.session.close()


_supervisor = BotSupervisor()


async def request_bot_reload(reason: str = "manual") -> None:
    await _supervisor.notify_reload(reason)


async def run_bot() -> None:
    await _supervisor.run_forever()
