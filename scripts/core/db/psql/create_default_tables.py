import sys

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy_utils import create_database, database_exists

from scripts.config import PostgresSQL
from scripts.logging import logger

conn_str = f"{PostgresSQL.POSTGRES_URI}/{PostgresSQL.DB_NAME}"
engine = create_engine(conn_str, pool_size=5, max_overflow=10, pool_pre_ping=True, pool_use_lifo=True)


def create_default_table_executor(_engine: Engine, metadata: MetaData):
    """
    Creates default tables in the database using the provided SQLAlchemy engine and metadata.
    Args:
        _engine (Engine): SQLAlchemy engine object.
        metadata (MetaData): SQLAlchemy metadata object.
    Raises:
        Exception: If an error occurs while creating the tables.
    Returns:
        None
    """
    try:
        if not database_exists(_engine.url):
            create_database(_engine.url)
        metadata.create_all(_engine, checkfirst=True)
    except Exception as e:
        logger.error(f"Error occurred while creating: {e}", exc_info=True)
        sys.exit()


def create_default_psql_dependencies(metadata: MetaData, engine_obj: Engine = None):
    """
    Creates default PostgresSQL dependencies.
    Args:
        metadata (MetaData): The metadata object containing the table definitions.
        engine_obj (Engine, optional): The SQLAlchemy engine object to use. Defaults to None.
    Raises:
        Exception: If an error occurs while creating the tables.

    """
    if not engine_obj:
        engine_obj = engine
    try:
        create_default_table_executor(engine_obj, metadata)
    except Exception as e:
        logger.error(f"Error occurred while creating: {e}", exc_info=True)
        raise e