from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine

from apps.api.app.models.base import Base
from apps.api.app.models import entities  # noqa: F401
from packages.shared.shared.config.settings import settings


engine = create_async_engine(settings.database_url, future=True, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _run_compat_migrations(conn)


async def _run_compat_migrations(conn: AsyncConnection) -> None:
    dialect = conn.dialect.name
    if dialect == "sqlite":
        result = await conn.execute(text("PRAGMA table_info(auto_reply_rules)"))
        columns = {row[1] for row in result.fetchall()}
        if "parse_mode" not in columns:
            await conn.execute(
                text("ALTER TABLE auto_reply_rules ADD COLUMN parse_mode VARCHAR(16) NOT NULL DEFAULT 'plain'")
            )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "join_verify_fail_action", "VARCHAR(32) NOT NULL DEFAULT 'kick'"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "join_verify_fail_mute_minutes", "INTEGER NOT NULL DEFAULT 30"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "join_verify_fail_ban_minutes", "INTEGER NOT NULL DEFAULT 1440"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "ad_block_action", "VARCHAR(32) NOT NULL DEFAULT 'mute'"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "ad_block_mute_minutes", "INTEGER NOT NULL DEFAULT 30"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "ad_block_ban_minutes", "INTEGER NOT NULL DEFAULT 1440"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "anti_spam_action", "VARCHAR(32) NOT NULL DEFAULT 'mute'"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "anti_spam_mute_minutes", "INTEGER NOT NULL DEFAULT 30"
        )
        await _add_sqlite_column_if_missing(
            conn, "group_configs", "anti_spam_ban_minutes", "INTEGER NOT NULL DEFAULT 1440"
        )
        return

    await _add_postgres_column_if_missing(
        conn, "auto_reply_rules", "parse_mode", "VARCHAR(16) NOT NULL DEFAULT 'plain'"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "join_verify_fail_action", "VARCHAR(32) NOT NULL DEFAULT 'kick'"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "join_verify_fail_mute_minutes", "INTEGER NOT NULL DEFAULT 30"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "join_verify_fail_ban_minutes", "INTEGER NOT NULL DEFAULT 1440"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "ad_block_action", "VARCHAR(32) NOT NULL DEFAULT 'mute'"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "ad_block_mute_minutes", "INTEGER NOT NULL DEFAULT 30"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "ad_block_ban_minutes", "INTEGER NOT NULL DEFAULT 1440"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "anti_spam_action", "VARCHAR(32) NOT NULL DEFAULT 'mute'"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "anti_spam_mute_minutes", "INTEGER NOT NULL DEFAULT 30"
    )
    await _add_postgres_column_if_missing(
        conn, "group_configs", "anti_spam_ban_minutes", "INTEGER NOT NULL DEFAULT 1440"
    )


async def _add_sqlite_column_if_missing(
    conn: AsyncConnection, table_name: str, column_name: str, definition: str
) -> None:
    result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
    columns = {row[1] for row in result.fetchall()}
    if column_name not in columns:
        await conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))


async def _add_postgres_column_if_missing(
    conn: AsyncConnection, table_name: str, column_name: str, definition: str
) -> None:
    result = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = :table_name AND column_name = :column_name"
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    if result.first() is None:
        await conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))
