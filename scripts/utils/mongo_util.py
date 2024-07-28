import re
from typing import Dict, List, Optional, Any

from pymongo import MongoClient

from scripts.config.constants import QueryConstants
from scripts.core.schemas.category_model import FetchCategories
from scripts.exceptions.module_exception import MongoException


class MongoConnect:
    def __init__(self, uri):
        try:
            self.uri = uri
            self.client = MongoClient(self.uri, connect=False)
        except Exception as e:
            raise MongoException(f"exception in insert function function as {e}") from e

    def __call__(self, *args, **kwargs):
        return self.client

    def __repr__(self):
        return f"Mongo Client(uri:{self.uri}, server_info={self.client.server_info()})"


class MongoCollectionBaseClass:
    def __init__(self, mongo_client, database, collection):
        self.client = mongo_client
        self.database = database
        self.collection = collection

    def __repr__(self):
        return f"{self.__class__.__name__}(database={self.database}, collection={self.collection})"

    def insert_one(self, data: Dict):
        """
        The function is used to inserting a document to a collection in a Mongo Database.
        :param data: Data to be inserted
        :return: Insert ID
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.insert_one(data)
            return response.inserted_id
        except Exception as e:
            raise MongoException(f"exception in insert function function as {e}") from e

    def insert_many(self, data: List):
        """
        The function is used to inserting documents to a collection in a Mongo Database.
        :param data: List of Data to be inserted
        :return: Insert IDs
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.insert_many(data)
            return response.inserted_ids
        except Exception as e:
            raise MongoException(f"exception in insert many function as {e}") from e

    def find(
        self,
        query: Dict,
        filter_dict: Optional[Dict] = None,
        sort=None,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> List:
        """
        The function is used to query documents from a given collection in a Mongo Database
        :param query: Query Dictionary
        :param filter_dict: Filter Dictionary
        :param sort: List of tuple with key and direction. [(key, -1), ...]
        :param skip: Skip Number
        :param limit: Limit Number
        :return: List of Documents
        """
        if sort is None:
            sort = []
        if filter_dict is None:
            filter_dict = {"_id": 0}
        database_name = self.database
        collection_name = self.collection
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            if len(sort) > 0:
                cursor = collection.find(query, filter_dict).sort(sort).skip(skip)
            else:
                cursor = collection.find(query, filter_dict).skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return cursor
        except Exception as e:
            raise MongoException(f"exception in mongo connection as {e}") from e

    def find_one(self, query: Dict, filter_dict: Optional[Dict] = None):
        try:
            database_name = self.database
            collection_name = self.collection
            if filter_dict is None:
                filter_dict = {"_id": 0}
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.find_one(query, filter_dict)
            return response or {}
        except Exception as e:
            raise MongoException(f"exception  in find function as {e}") from e

    def update_one(self, query: Dict, data: Dict, upsert: bool = False):
        """
        :param upsert:
        :param query:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            if "$set" in data:
                data = data["$set"]
            response = collection.update_one(query, {"$set": data}, upsert=upsert)
            return response.modified_count
        except Exception as e:
            raise MongoException(f"exception  in update function as {e}") from e

    def update_many(self, query: Dict, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            if "$set" in data:
                data = data["$set"]
            response = collection.update_many(query, {"$set": data}, upsert=upsert)
            return response.modified_count
        except Exception as e:
            raise MongoException(f"exception in aggregate function as {e}") from e

    def delete_many(self, query: Dict):
        """
        :param query:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.delete_many(query)
            return response.deleted_count
        except Exception as e:
            raise MongoException(f"exception  in connecting {e}") from e

    def delete_one(self, query: Dict):
        """
        :param query:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.delete_one(query)
            return response.deleted_count
        except Exception as e:
            raise MongoException(
                f"exception  in delete function of mongo as {e}"
            ) from e

    def aggregate(self, pipelines: List):
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            return collection.aggregate(pipelines)
        except Exception as e:
            raise MongoException(f"exception in aggregate function as {e}") from e



