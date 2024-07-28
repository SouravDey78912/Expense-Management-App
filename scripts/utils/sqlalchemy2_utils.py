from enum import Enum
from typing import Generic, List, Tuple, TypeVar

import pandas as pd
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, func, insert, select, update, desc, asc, text
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.orm import DeclarativeBase, Session, Query
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from scripts.config.constants import QueryConstants
from scripts.core.db.psql import Base
from scripts.core.schemas.transaction_model import FetchTransactionModel
from scripts.logging import logger

TableType = TypeVar("TableType", bound=DeclarativeBase)


class QueryType(str, Enum):
    """
    An enumeration representing the different types of queries that can be executed.

    Attributes:
        JSON (str): The query result will be returned as a JSON object.
        PANDAS (str): The query result will be returned as a Pandas DataFrame.
    """

    JSON = "json"
    PANDAS = "pandas"


T = TypeVar('T', bound=Base)


class SqlAlchemyUtil(Generic[T]):
    """
    A utility class for performing SQL operations using SQLAlchemy V2.
    """

    def __init__(self, session: Session, table: TableType = None):
        """
        Initializes a new instance of the SqlAlchemyUtil class.

        Args:
            session (Session): The SQLAlchemy session object.
            table (TableType, optional): The SQLAlchemy declarative base object. Defaults to None.
        """
        self.session = session
        self.table = table

    def close(self):
        """
        Closes the SQLAlchemy session.
        """
        logger.debug("Closing SQL session!")
        self.session.close()

    def insert(self, data: dict | list[dict], return_keys: List[str] = None, table: TableType = None):
        """
        Inserts a single row into the database.

        Args:
            data (dict): A dictionary containing the data to be inserted.
            return_keys (List[str], optional): A list of column names to return after the insert. Defaults to None.
            table (TableType, optional): The SQLAlchemy declarative base object. Defaults to None.

        Returns:
            A list of dictionaries containing the inserted data.
        """
        table = table or self.table
        return_keys = return_keys or []
        try:
            insert_stmt = insert(table).values(data).returning(*(getattr(table.c, key) for key in return_keys))
            self.session.execute(insert_stmt)
            self.session.commit()
        except Exception as e:
            logger.error(f"Error occurred while inserting: {e}", exc_info=True)
            raise e

    def update_with_where(self, data: dict, where_conditions: List, table: TableType = None):
        """
        Updates rows in the database based on the given conditions.

        Args:
            data (dict): A dictionary containing the data to be updated.
            where_conditions (List): A list of conditions to filter the data.
            table (TableType, optional): The SQLAlchemy declarative base object. Defaults to None.
        """
        table = table or self.table
        try:
            update_stmt = update(table).values(data).where(*where_conditions)
            self.session.execute(update_stmt)
            self.session.commit()
        except Exception as e:
            logger.error(f"Error occurred while updating: {e}", exc_info=True)
            raise e

    def upsert(self, insert_json: dict, primary_keys: List[str] = None, table: TableType = None):
        """
        Inserts or updates a row in the database.

        Args:
            insert_json (dict): A dictionary containing the data to be inserted or updated.
            primary_keys (List[str], optional): A list of primary key column names. Defaults to None.
            table (TableType, optional): The SQLAlchemy declarative base object. Defaults to None.
        """
        table = table or self.table
        try:
            insert_statement = (
                postgres_insert(table)
                .values(**insert_json)
                .on_conflict_do_update(index_elements=primary_keys, set_=insert_json)
            )
            self.session.execute(insert_statement)
            self.session.commit()
        except Exception as e:
            logger.error(f"Error while upserting the record {e}", exc_info=True)
            raise e

    def delete(self, where_conditions: List, table: TableType = None):
        """
        Deletes rows from the database based on the given conditions.

        Args:
            where_conditions (List): A list of conditions to filter the data.
            table (TableType, optional): The SQLAlchemy declarative base object. Defaults to None.
        """
        table = table or self.table
        try:
            delete_stmt = delete(table).where(*where_conditions)
            self.session.execute(delete_stmt)
            self.session.commit()
        except Exception as e:
            logger.error(f"Error occurred while deleting: {e}", exc_info=True)
            raise e

    def _get_columns(self, columns: List, table: TableType) -> List:
        columns_updated = []
        for column in columns:
            if isinstance(column, str):
                columns_updated.append(getattr(table, column))
            elif isinstance(column, DeclarativeAttributeIntercept):
                columns_updated.extend(list(column.__table__.columns))
            else:
                columns_updated.append(column)
        return columns_updated

    def _build_select_query(
            self,
            table: TableType,
            where_conditions: List,
            offset: int = None,
            columns: Tuple[str] = None,
            order_by: List = None,
            group_by: List = None,
    ):
        """
        Builds a select query based on the given conditions.

        Args:
            table (TableType): The SQLAlchemy declarative base object.
            where_conditions (List): A list of conditions to filter the data.
            columns (Tuple[str], optional): A tuple of column names to select. Defaults to None.

        Returns:
            The built select query.
        """
        order_by = order_by or []
        group_by = group_by or []
        select_stmt = select(*table.__table__.columns)
        if columns:
            select_stmt = select_stmt.with_only_columns(*self._get_columns(columns, table))
        return select_stmt.where(*where_conditions).order_by(*order_by).group_by(*group_by).offset(offset)

    def _get_count(self, table: TableType, where_conditions: List):
        """
        Returns the count of rows in the given table.

        Args:
            table (TableType): The SQLAlchemy declarative base object.
            where_conditions (List): A list of conditions to filter the data.

        Returns:
            The count of rows in the given table.
        """
        count_query = select(table).with_only_columns(func.count()).order_by(None).where(*where_conditions)
        return self.session.execute(count_query).scalar()

    def select_from_table(
            self,
            where_conditions: List,
            columns: Tuple[str] = None,
            select_one: bool = False,
            offset: int = None,
            limit: int = None,
            return_count: bool = False,
            return_type: QueryType = QueryType.JSON,
            order_by: List = None,
            group_by: List = None,
            table: TableType = None,
    ):
        """
        Selects data from a table based on the given conditions.
        Args:
            where_conditions (List): A list of conditions to filter the data by.
            columns (Tuple[str], optional): A tuple of column names to select. Defaults to None.
            select_one (bool, optional): Whether to select only one row. Defaults to False.
            offset (int, optional): The number of rows to skip. Defaults to None.
            limit (int, optional): The maximum number of rows to return. Defaults to None.
            return_count (bool, optional): Whether to return the count of rows. Defaults to False.
            return_type (QueryType, optional): The type of query to return. Defaults to QueryType.JSON.
            table (TableType, optional): The table to select from. Defaults to None.
        Returns:
            The selected data.
        """
        table = table or self.table
        try:
            select_stmt = self._build_select_query(table, where_conditions, offset, columns, order_by, group_by)
            if select_one:
                return jsonable_encoder(self.session.execute(select_stmt).mappings().first())
            results = self.fetch_by_query(select_stmt.limit(limit), return_type)
            if return_count:
                return (self._get_count(table, where_conditions), results)
            return pd.DataFrame if (return_type == QueryType.PANDAS and results is None) else results
        except Exception as e:
            logger.error(f"Error occurred while fetching: {e}", exc_info=True)
            raise e

    def fetch_as_pandas(self, query):
        """
        Fetches data from the database using pandas or connectorx library.
        Args:
            query (str): SQL query to execute.
        Returns:
            pandas.DataFrame: DataFrame containing the results of the query.
        Raises:
            ImportError: If neither pandas nor connectorx library is installed.
            Exception: If an error occurs while fetching data using pandas or connectorx.
        """
        try:
            try:
                import connectorx as cx

                query = str(query.compile(compile_kwargs={"literal_binds": True}))
                return cx.read_sql(
                    self.session.bind.url.render_as_string(hide_password=False).replace(
                        "postgresql+psycopg://", "postgresql://"
                    ),
                    query,
                )
            except ImportError:
                logger.error("Connectorx not installed, Using Fall back to pandas")
            try:
                import pandas as pd

                return pd.read_sql(query, self.session.bind)
            except ImportError as ie:
                logger.error("Pandas not installed, Failed to fetch using pandas")
                raise ie
        except Exception as e:
            logger.error(f"Error occurred while fetching using pandas: {e}")

    def fetch_as_json(self, query:Query):
        """
        Executes the given SQL query and returns the result as a list of dictionaries or dictionaries.
        Args:
            query (str): The SQL query to execute.
        Returns:
            list: A list of dictionaries representing the result of the query.
        Raises:
            Exception: If an error occurs while fetching data.
        """
        try:
            _ = str(query.compile(compile_kwargs={"literal_binds": True}))
            data = jsonable_encoder(self.session.execute(query).mappings().all())
            return data[0] if len(data) == 1 else data
        except Exception as e:
            logger.error(f"Error occurred while fetching data: {e}")

    def fetch_by_query(self, query, query_type: QueryType = QueryType.JSON):
        """
        Fetches data from the database using the provided query and returns the result in the specified format.
        Args:
            query (str): The SQL query to execute.
            query_type (QueryType, optional): The format in which to return the result. Defaults to QueryType.JSON.

        Returns:
            The result of the query in the specified format.
        """
        try:
            callable_func = getattr(self, f"fetch_as_{query_type.value}")
            return callable_func(query)
        except Exception as e:
            logger.error(f"Error occurred while fetching: {e}")


class SQLQueryBuilder:
    def __init__(self, table):
        self.table = table

    def add_filters(self, query, input_data: FetchTransactionModel) -> Query:
        if input_data.filters.sortModel:
            key_column_map = QueryConstants.key_column_map
            for each_sort in input_data.filters.sortModel:
                each_sort["colId"] = key_column_map.get(
                    each_sort["colId"], each_sort["colId"]
                )
                if hasattr(self.table, each_sort["colId"]):
                    column = getattr(self.table, each_sort["colId"])
                    if each_sort["sort"].lower() == "desc":
                        query = query.order_by(desc(column))
                    elif each_sort["sort"].lower() == "asc":
                        query = query.order_by(asc(column))
                elif each_sort["colId"].startswith('meta'):
                    json_field = each_sort["colId"].split(".")[1]  # remove 'meta->>' prefix
                    if each_sort["sort"].lower() == 'desc':
                        query = query.order_by(desc(text(f"meta->>'{json_field}'")))
                    else:
                        query = query.order_by(asc(text(f"meta->>'{json_field}'")))
        if input_data.filters.filterModel:
            query = self.query_builder(
                query=query,
                filter_dict=input_data.filters.filterModel
            )
        return query

    def query_builder(self, query, filter_dict: dict):
        for _key, _value in filter_dict.items():
            if hasattr(self.table, _key):
                column = getattr(self.table, _key)
                if isinstance(_value, str) and '%' in _value:
                    query = query.filter(column.like(_value))
                else:
                    query = query.filter(column == _value)
        return query
