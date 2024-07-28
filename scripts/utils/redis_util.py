import redis


class RedisConnector:
    def __init__(self, redis_uri: str):
        self.redis_uri = redis_uri

    def connect(self, db: int, decoded_response: bool = True):
        """
        Connects to a Redis database using the provided database number and settings.
        Args:
            db: Integer representing the database number to connect to.
            decoded_response: Boolean indicating whether responses should be decoded (default True).
        Returns:
            Redis: Redis connection object.
        """
        return redis.from_url(
            url=self.redis_uri, db=db, decode_responses=decoded_response
        )
