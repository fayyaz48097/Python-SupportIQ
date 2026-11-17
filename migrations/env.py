from logging.config import fileConfig

from alembic import context
from sqlalchemy import URL, create_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.base import Base
from app.tickets import models  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def get_migration_database_url() -> URL:
    if not settings.migration_db_user or not settings.migration_db_password:
        raise RuntimeError(
            "Migration database credentials are missing. "
            "Configure MIGRATION_DB_USER and MIGRATION_DB_PASSWORD in .env."
        )

    return URL.create(
        drivername="mysql+pymysql",
        username=settings.migration_db_user,
        password=settings.migration_db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        query={"charset": "utf8mb4"},
    )


def run_migrations_offline() -> None:
    context.configure(
        url=get_migration_database_url().render_as_string(
            hide_password=False
        ),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_migration_database_url(),
        poolclass=NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()