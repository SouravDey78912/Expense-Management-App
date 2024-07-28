from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class _Services(BaseSettings):
    PORT: int = Field(default=6869, validation_alias="service_port")
    HOST: str = Field(default="0.0.0.0", validation_alias="service_host")
    SECURE_ACCESS: bool = Field(default=True)


class _Redis(BaseSettings):
    REDIS_URI: str = Field()


class _PostgresSQL(BaseSettings):
    POSTGRES_URI: str
    DB_NAME: Optional[str] = "expense_tracker"

    @field_validator("POSTGRES_URI", mode="before")
    def validate_my_field(cls, value):
        value = value.strip("/")
        import urllib.parse
        unquoted_postgres_uri = urllib.parse.unquote(value)
        value = urllib.parse.quote(unquoted_postgres_uri, safe=":/@")
        value = value.replace("postgresql://", "postgresql+psycopg://")
        return value


class _Mongo(BaseSettings):
    MONGO_URI: str = Field()


Services = _Services()
Redis = _Redis()
Mongo = _Mongo()
PostgresSQL = _PostgresSQL()

__all__ = ["Services", "Redis", "Mongo", "PostgresSQL"]