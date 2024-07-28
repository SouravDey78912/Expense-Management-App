from datetime import timezone, datetime

import shortuuid
from sqlalchemy import select

from scripts.core.db.mongo import mongo_client
from scripts.core.db.mongo.expense_tracker.user import UserMongo
from scripts.core.schemas.category_model import CreateCategoriesModel, MetaData, FetchCategories
from scripts.exceptions.module_exception import CustomError
from scripts.logging import logger
from scripts.utils.sqlalchemy2_utils import SqlAlchemyUtil, SQLQueryBuilder


class CategoryHandler(SQLQueryBuilder):
    def __init__(self, session, table):
        super().__init__(table)
        self.user_mongo = UserMongo(mongo_client=mongo_client)
        self.session = session
        self.table = table

    def create_categories(self, request_data: CreateCategoriesModel, user_id: str) -> str:
        try:
            request_data.category_id = shortuuid.uuid()
            sql_conn = SqlAlchemyUtil(session=self.session, table=self.table)
            if sql_conn.select_from_table(
                    where_conditions=[self.table.category_name == request_data.category_name]
            ):
                raise CustomError("Category already exists!!")
            request_data.meta = MetaData(
                created_by=user_id,
                created_at=int(datetime.now(timezone.utc).timestamp()),
            )
            sql_conn.insert(request_data.model_dump())
            return request_data.category_id
        except Exception as e:
            logger.info(f"Error while creating category : {str(e)}")
            raise

    def update_categories(self, request_data: CreateCategoriesModel, user_id):
        """
        Updates a category with the provided data.
        Args:
            request_data (CreateCategoriesModel): The data to update the category with.
            user_id: The ID of the user performing the update.
        Returns:
            None
        Raises:
            CustomError: If the category_id provided in the request_data is invalid.
        """
        try:
            sql_conn = SqlAlchemyUtil(session=self.session, table=self.table)
            if category_data := sql_conn.select_from_table(
                    where_conditions=[self.table.category_id == request_data.category_id]
            ):
                request_data.meta = MetaData(
                    created_at=category_data["meta"]["created_at"],
                    created_by=category_data["meta"]["created_by"],
                    updated_by=user_id,
                    updated_at=int(datetime.now(timezone.utc).timestamp()),
                )
                sql_conn.update_with_where(data=request_data.model_dump(),
                                           where_conditions=[self.table.category_id == request_data.category_id]
                                           )
            else:
                raise CustomError("Invalid category_id !!")
        except Exception as e:
            logger.info(f"Error while creating category : {str(e)}")
            raise

    def fetch_categories(self, request_data: FetchCategories) -> list:
        """
        Fetches category based on the provided request data.
        Args:
            request_data: Data containing the user ID for fetching categories.
        Returns:
            List: List of category fetched based on the request data.
        Raises:
            Any Exception raised during the task fetching process.
        """
        try:
            query = (select(self.table))
            query = self.add_filters(query=query, input_data=request_data)
            if task_data := SqlAlchemyUtil(session=self.session, table=self.table).fetch_as_json(query):
                return task_data
            logger.debug("No data found")
            return []
        except Exception as e:
            logger.info(f"Error while fetching categories : {str(e)}")
            raise


