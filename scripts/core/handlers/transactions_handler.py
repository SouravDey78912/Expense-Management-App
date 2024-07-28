from datetime import datetime, timezone

import shortuuid
from sqlalchemy import select

from scripts.core.db.mongo import mongo_client
from scripts.core.db.mongo.expense_tracker.user import UserMongo
from scripts.core.db.psql.db_models import Transactions
from scripts.core.schemas import MetaData
from scripts.core.schemas.transaction_model import CreateTransactionModel, FetchTransactionModel
from scripts.logging import logger
from scripts.utils.sqlalchemy2_utils import SqlAlchemyUtil, SQLQueryBuilder


class TransactionHandler(SQLQueryBuilder):
    def __init__(self, session, table):
        super().__init__(table)
        self.user_mongo = UserMongo(mongo_client=mongo_client)
        self.session = session

    def create_transaction(self, request_data: CreateTransactionModel, user_id: str) -> str:
        """
        Creates a transaction with the provided data.
        create_transaction method generates a transaction ID, sets metadata, inserts the data into a database table, and returns the category ID.
        Args:
            request_data: Data for creating the transaction.
            user_id: ID of the user creating the transaction.
        Returns:
            str: Category ID of the created transaction.
        Raises:
            Any Exception raised during the transaction creation process.
        """
        try:
            request_data.t_id = shortuuid.uuid()
            request_data.meta = MetaData(
                created_by=user_id,
                created_at=int(datetime.now(timezone.utc).timestamp()),
            )
            SqlAlchemyUtil(session=self.session, table=Transactions).insert(request_data.model_dump())
            return request_data.category_id
        except Exception as e:
            logger.info(f"Error while creating transaction : {str(e)}")
            raise

    def fetch_transaction(self, request_data: FetchTransactionModel) -> list:
        """
        Fetches categories based on the provided request data.
        fetch_transaction method fetches transaction based on the provided request data.
        Args:
            request_data: Data containing the user ID for fetching transactions.
        Returns:
            List: List of categories fetched based on the request data.
        Raises:
            Any Exception raised during the transaction fetching process.
        """
        try:
            query = (select(self.table))
            query = self.add_filters(query=query, input_data=request_data)
            if task_data := SqlAlchemyUtil(session=self.session, table=Transactions).fetch_as_json(query):
                return task_data
            logger.debug("No data found")
            return []
        except Exception as e:
            logger.info(f"Error while fetch transaction : {str(e)}")
            raise
