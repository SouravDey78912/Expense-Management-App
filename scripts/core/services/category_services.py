from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from scripts.api import Endpoints
from scripts.core.db.psql import get_session
from scripts.core.db.psql.db_models import Categories
from scripts.core.handlers.category_handler import CategoryHandler
from scripts.core.schemas import DefaultResponseSchema, DefaultFailureSchema
from scripts.core.schemas.category_model import CreateCategoriesModel, FetchCategories
from scripts.utils.authorisation import MetaInfoSchema
from typing_extensions import Annotated

category_router = APIRouter(prefix=Endpoints.api_category)


@category_router.post(Endpoints.api_create)
async def create_categories(request_data: CreateCategoriesModel,session: Annotated[Session, Depends(get_session)], meta: MetaInfoSchema):
    try:
        task_handler = CategoryHandler(session=session, table=Categories)
        return DefaultResponseSchema(
            data=task_handler.create_categories(request_data, user_id=meta.user_id)
        )
    except Exception as e:
        return DefaultFailureSchema(message="Failed to create categories", error=str(e))


@category_router.post(Endpoints.api_update)
async def update_categories(request_data: CreateCategoriesModel, session: Annotated[Session, Depends(get_session)], meta: MetaInfoSchema):
    try:
        task_handler = CategoryHandler(session=session, table=Categories)
        return DefaultResponseSchema(
            data=task_handler.update_categories(request_data, user_id=meta.user_id)
        )
    except Exception as e:
        return DefaultFailureSchema(message="Failed to update categories", error=str(e))


@category_router.post(Endpoints.api_fetch)
async def fetch_categories(request_data: FetchCategories, session: Annotated[Session, Depends(get_session)], meta: MetaInfoSchema):
    try:
        task_handler = CategoryHandler(session=session, table=Categories)
        return DefaultResponseSchema(data=task_handler.fetch_categories(request_data))
    except Exception as e:
        return DefaultFailureSchema(message="Failed to fetch categories", error=str(e))
