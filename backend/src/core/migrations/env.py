import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection

from alembic import context

ROOT_DIR = Path(__file__).parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.database import Base, get_database_url

from src.modules.user.models.orm.user_orm import UserORM
from src.modules.chats.models.orm.chat_orm import ChatORM
from src.modules.messages.models.orm.message_orm import MessageORM
from src.modules.participants.models.orm.participant_orm import ParticipantORM
from src.modules.media.models.media_orm import MediaORM
from src.modules.profiles_custom.models.orm.profile_custom_orm import ProfileCustomORM

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sync_url = (
    get_database_url()
    .replace("+aiosqlite", "")
    .replace("+asyncpg", "+psycopg")
)
config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    sync_engine = create_engine(sync_url, poolclass=pool.NullPool)
    with sync_engine.connect() as connection:
        do_run_migrations(connection)
    sync_engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
