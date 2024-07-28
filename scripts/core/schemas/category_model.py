from typing import Optional

from pydantic import BaseModel


from scripts.core.schemas import MetaData


class CreateCategoriesModel(BaseModel):
    category_id: Optional[str] = ""
    category_name: str
    description: Optional[str] = ""
    meta: Optional[MetaData] = None


class FilterModel(BaseModel):
    filterModel: Optional[dict] = {}
    sortModel: Optional[list] = []


class FetchCategories(BaseModel):
    user_id: str
    filters: Optional[FilterModel] = FilterModel()
