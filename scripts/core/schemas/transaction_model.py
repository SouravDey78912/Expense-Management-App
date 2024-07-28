from typing import Optional

from pydantic import BaseModel
from scripts.core.schemas import MetaData


class CreateTransactionModel(BaseModel):
    t_id: Optional[str] = ""
    category_id: str
    amount: float
    description: Optional[str] = ""
    meta: Optional[MetaData] = None


class FilterModel(BaseModel):
    filterModel: Optional[dict] = {}
    sortModel: Optional[list] = []


class FetchTransactionModel(BaseModel):
    user_id: str
    filters: Optional[FilterModel] = FilterModel()
