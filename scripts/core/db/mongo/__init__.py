from scripts.config import Mongo
from scripts.utils.mongo_util import MongoConnect

mongo_client = MongoConnect(uri=Mongo.MONGO_URI)()
