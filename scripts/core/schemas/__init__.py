from typing import Any, Optional

from pydantic import BaseModel, Field


class MetaData(BaseModel):
    created_by: Optional[str] = ""
    created_at: Optional[int] = 0
    updated_at: Optional[int] = 0
    updated_by: Optional[str] = ""


class DefaultResponseSchema(BaseModel):
    status: str = Field(default="success")
    message: str = Field(default="success")
    data: Any = Field(default=None)


class DefaultFailureSchema(DefaultResponseSchema):
    status: str = Field(default="failure")
    message: str = Field(default="failure")
    error: str = Field(default=None)
