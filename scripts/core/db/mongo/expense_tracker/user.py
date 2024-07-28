from scripts.config.constants import DBMapping, CollectionMap
from scripts.utils.mongo_util import MongoCollectionBaseClass


class UserMongo(MongoCollectionBaseClass):
    def __init__(self, mongo_client):
        super().__init__(
            mongo_client, database=DBMapping.expense_manager, collection=CollectionMap.user
        )
