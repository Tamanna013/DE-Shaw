import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
import sys

# Add the parent directory of shared to PYTHONPATH so we can import shared.db.models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.db.base import Base

# Import all models to ensure they are registered with Base.metadata
from shared.db.models.users import UserModel, BlockedEmailDomainModel
from shared.db.models.teams import TeamModel, UserProfileModel
from shared.db.models.repositories import RepositoryModel
from shared.db.models.test_runs import TestRunModel
from shared.db.models.test_cases import TestCaseModel
from shared.db.models.test_case_executions import TestCaseExecutionModel
from shared.db.models.failures import FailureModel
from shared.db.models.embeddings import FailureEmbeddingModel
from shared.db.models.flaky_test_signals import FlakyTestSignalModel
from shared.db.models.commits import CommitModel
from shared.db.models.commit_test_correlations import CommitTestCorrelationModel
from shared.db.models.notifications import NotificationModel
from shared.db.models.audit_log import AuditLogModel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/testlens")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        # Manually enable pgvector before tables are created in the first migration
        context.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        context.run_migrations()

async def run_migrations_online() -> None:
    url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/testlens")
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
