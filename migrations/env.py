from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from sqlmodel import SQLModel
from salus.config import settings
from salus.models import MetricType
from salus.models.user import User
from salus.models.user_identity import UserIdentity
from salus.models.measurement import Measurement
from salus.models.goal import Goal
from salus.models.dashboard import DashboardWidget
from salus.models.api_token import ApiToken
from salus.models.system_config import SystemConfig
from salus.models.insight import Insight

# Dynamically load plugins to register custom tables/models in SQLModel.metadata
try:
    from salus.services.plugin.manager import PluginManager
    from salus.repositories.unit_of_work import SqlUnitOfWork
    from sqlalchemy import create_engine
    from sqlmodel import Session
    
    dummy_engine = create_engine("sqlite://")
    dummy_session = Session(dummy_engine)
    dummy_uow = SqlUnitOfWork(dummy_session)
    pm = PluginManager(plugins_dir="src/salus/plugins", uow=dummy_uow)
    pm.discover_and_load_all()
except Exception as e:
    import logging
    logging.warning(f"Could not load plugins during migrations environment setup: {e}")

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from sqlalchemy import create_engine
    connectable = create_engine(settings.database_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
