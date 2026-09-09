import asyncio
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base
from app.models import Category, Order, OrderItem, Post, Product, Profile, User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    config_path = Path(config.config_file_name)
    if config_path.exists():
        try:
            fileConfig(config.config_file_name, disable_existing_loggers=False)
        except (KeyError, ValueError):
            pass

# NOTE: DATABASE_URL is a computed property in app/core/config.py,
# assembled from POSTGRES_USER/PASSWORD/HOST/PORT/DB — keep it uppercase
# to match the Settings model.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

# Detect column type / default changes too, not just new/removed tables.
COMPARE_OPTS = {
    "compare_type": True,
    "compare_server_default": True,
}


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **COMPARE_OPTS,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        **COMPARE_OPTS,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()