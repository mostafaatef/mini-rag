from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()


# Look for requirements.txt to identify project root
def find_root(start_path):
    for parent in start_path.parents:
        if (parent / "requirements.txt").exists():
            return parent
    return start_path.parents[6]  # Fallback


project_root = find_root(current_file)
sys.path.append(str(project_root))

# Robust import for SqlAlchemyBase
try:
    from src.models.schemes.mini_rag_db.sql.schemes.mini_rag_base import SqlAlchemyBase
except ImportError:
    from models.schemes.mini_rag_db.sql.schemes.mini_rag_base import SqlAlchemyBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = SqlAlchemyBase.metadata


def get_url():
    # Priority: Env var, then .ini file
    url = os.getenv("VECTOR_POSTGRES_DB_URL")
    if not url:
        user = os.getenv("POSTGRES_USERNAME", "minirag")
        password = os.getenv("POSTGRES_PASSWORD", "minirag")
        host = os.getenv("POSTGRES_HOST", "pgvector")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_MAIN_DATABASE", "mini_rag")
        url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Override sqlalchemy.url with dynamic URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
