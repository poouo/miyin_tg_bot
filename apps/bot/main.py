import asyncio

from apps.bot.bot_app.dispatcher import run_bot


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()

