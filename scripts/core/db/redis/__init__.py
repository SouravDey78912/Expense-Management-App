from scripts.config import Redis
from scripts.utils.redis_util import RedisConnector

# Establish a connection to Redis
redis_client = RedisConnector(Redis.REDIS_URI)

login_db = redis_client.connect(db=0)
