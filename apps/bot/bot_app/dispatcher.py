import asyncio
import logging
from contextlib import suppress
from functools import lru_cache

from aiogram import Bot, Dispatcher, F
from aiogram.methods import GetUpdates
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)
from aiogram.utils.token import TokenValidationError, validate_token

from apps.api.app.services.runtime_config_service import get_runtime_config
from apps.api.app.services.runtime_health import record_bot
from apps.bot.bot_app.handlers.commands import router as command_router
from apps.bot.bot_app.handlers.group_events import bot_ad_message_handler, group_lock_middleware, router as group_router
from apps.bot.bot_app.tasks import ai_ad_flush_task, kick_unverified_task, recover_mute_task, rss_poll_task

logger = logging.getLogger(__name__)


async def track_polling(make_request, bot, method):
    if not isinstance(method, GetUpdates):
        return await make_request(bot, method)
    try:
        result = await make_request(bot, method)
    except Exception:
        record_bot("error")
        raise
    record_bot("online")
    return result


USER_COMMANDS = [
    BotCommand(command="help", description="帮助"),
    BotCommand(command="ask", description="AI"),
    BotCommand(command="rules", description="群规则"),
    BotCommand(command="notes", description="群笔记"),
    BotCommand(command="get", description="读取笔记"),
    BotCommand(command="warns", description="我的警告"),
    BotCommand(command="report", description="举报"),
    BotCommand(command="id", description="查看ID"),
    BotCommand(command="afk", description="离开"),
]

ADMIN_COMMANDS = [
    *USER_COMMANDS,
    BotCommand(command="ban", description="拉黑"),
    BotCommand(command="kick", description="移除"),
    BotCommand(command="mute", description="禁言"),
    BotCommand(command="unban", description="解封"),
    BotCommand(command="unmute", description="解禁"),
    BotCommand(command="warn", description="警告"),
    BotCommand(command="resetwarn", description="清警告"),
    BotCommand(command="setrules", description="设规则"),
    BotCommand(command="save", description="存笔记"),
    BotCommand(command="lock", description="锁消息"),
    BotCommand(command="unlock", description="解锁"),
    BotCommand(command="adminlist", description="管理员"),
    BotCommand(command="pin", description="置顶"),
    BotCommand(command="unpin", description="取消置顶"),
    BotCommand(command="welcome", description="欢迎"),
    BotCommand(command="goodbye", description="退群"),
    BotCommand(command="gban", description="全局封禁"),
    BotCommand(command="disable", description="禁用指令"),
    BotCommand(command="purge", description="清理"),
]


async def setup_bot_commands(bot: Bot) -> None:
    runtime = await get_runtime_config()
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeAllChatAdministrators())
    for admin_id in runtime.telegram_admin_id_list:
        await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id))


@lru_cache(maxsize=1)
def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    for observer in (dp.message, dp.edited_message):
        observer.outer_middleware(group_lock_middleware)
        observer.register(bot_ad_message_handler, F.from_user.is_bot, lambda message: message.sender_chat is None)
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
        try:
            while True:
                try:
                    await asyncio.wait_for(self._reload_event.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass

                self._reload_event.clear()
                async with self._lock:
                    if not await self._check_polling_health():
                        await self._sync_with_runtime()
        finally:
            await self._stop_polling("shutdown")

    async def _sync_with_runtime(self) -> None:
        runtime = await get_runtime_config()
        token = runtime.telegram_bot_token.strip()

        if not token or token == "replace_me":
            record_bot("not_configured")
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
            record_bot("error")
            if token != self._invalid_token:
                logger.error("TELEGRAM_BOT_TOKEN is invalid; bot polling is disabled.")
            self._invalid_token = token
            await self._stop_polling("token_invalid")
            return

        self._invalid_token = ""
        await self._stop_polling("token_changed")
        self._running_token = token
        record_bot("starting")
        self._polling_task = asyncio.create_task(self._polling_loop(token), name="tg-bot-polling")
        logger.info("Bot polling started.")

    async def _check_polling_health(self) -> bool:
        if self._polling_task is None:
            return False
        if not self._polling_task.done():
            return False

        task = self._polling_task
        self._polling_task = None
        self._running_token = ""
        record_bot("error")
        with suppress(asyncio.CancelledError):
            exc = task.exception()
            if exc:
                logger.error("Bot polling stopped unexpectedly: %s", exc)
            else:
                logger.warning("Bot polling task exited.")
        return True

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
        bot.session.middleware(track_polling)
        dp = build_dispatcher()
        recover_task = asyncio.create_task(recover_mute_task(bot), name="recover-mute-task")
        kick_task = asyncio.create_task(kick_unverified_task(bot), name="kick-unverified-task")
        rss_task = asyncio.create_task(rss_poll_task(bot), name="rss-poll-task")
        ai_ad_task = asyncio.create_task(ai_ad_flush_task(bot), name="ai-ad-flush-task")
        try:
            await setup_bot_commands(bot)
            await dp.start_polling(bot, handle_signals=False, close_bot_session=False)
        finally:
            recover_task.cancel()
            kick_task.cancel()
            rss_task.cancel()
            ai_ad_task.cancel()
            with suppress(asyncio.CancelledError):
                await recover_task
            with suppress(asyncio.CancelledError):
                await kick_task
            with suppress(asyncio.CancelledError):
                await rss_task
            with suppress(asyncio.CancelledError):
                await ai_ad_task
            await bot.session.close()


_supervisor = BotSupervisor()


async def request_bot_reload(reason: str = "manual") -> None:
    await _supervisor.notify_reload(reason)


async def run_bot() -> None:
    await _supervisor.run_forever()
