import datetime
from typing import Any

from sqlalchemy import create_engine, TIMESTAMP, JSON
from sqlalchemy.orm import DeclarativeBase, Session

from scripts.utils.authorisation import MetaInfoSchema
from scripts.config import PostgresSQL


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """

    type_annotation_map = {datetime.datetime: TIMESTAMP(timezone=True), dict[str, Any]: JSON}


async def get_session():
    """
    This function retrieves the database connection for a given project_id.
    It creates the default tables if they don't exist and returns a session object for the database.
    Args:
        request_data (Request): The request object containing the project_id.
    Yields:
        Session: A session object for the database.
        :param meta:

    """
    from scripts.core.db.psql.create_default_tables import create_default_psql_dependencies
    conn_str = f"{PostgresSQL.POSTGRES_URI}/{PostgresSQL.DB_NAME}"
    engine = create_engine(
        conn_str,
        connect_args={"connect_timeout": 2},
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_use_lifo=True,
        future=True,
        echo=True
    )
    create_default_psql_dependencies(metadata=Base.metadata, engine_obj=engine)
    try:
        with Session(bind=engine, autocommit=False, autoflush=False, future=True) as session:
            yield session
    finally:
        engine.dispose()
