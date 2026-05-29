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
        return

    result = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'auto_reply_rules' AND column_name = 'parse_mode'"
        )
    )
    has_parse_mode = result.first() is not None
    if not has_parse_mode:
        await conn.execute(
            text("ALTER TABLE auto_reply_rules ADD COLUMN parse_mode VARCHAR(16) NOT NULL DEFAULT 'plain'")
        )
