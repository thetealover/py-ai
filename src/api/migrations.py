import logging
from alembic import command
from alembic.config import Config
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)


def run_migrations_sync(sync_pool: ConnectionPool):
    """
    A synchronous function to run Alembic migrations using a shared pool.
    """
    logger.info("Running database migrations...")
    alembic_cfg = Config("alembic.ini")

    alembic_cfg.attributes["connection"] = sync_pool.getconn()

    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations complete.")
    finally:
        sync_pool.putconn(alembic_cfg.attributes["connection"])
