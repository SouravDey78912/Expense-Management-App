from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from scripts.api import Endpoints
from scripts.core.db.psql import get_session
from scripts.core.db.psql.db_models import Transactions
from scripts.core.handlers.transactions_handler import TransactionHandler
from scripts.core.schemas import DefaultResponseSchema, DefaultFailureSchema
from scripts.core.schemas.category_model import FetchCategories
from scripts.core.schemas.transaction_model import CreateTransactionModel
from scripts.utils.authorisation import MetaInfoSchema

transactions_router = APIRouter(prefix=Endpoints.api_transaction)


@transactions_router.post(Endpoints.api_create)
async def create_transactions(request_data: CreateTransactionModel, session: Annotated[Session, Depends(get_session)], meta: MetaInfoSchema):
    try:
        t_handler = TransactionHandler(session=session, table=Transactions)
        return DefaultResponseSchema(
            data=t_handler.create_transaction(request_data, user_id=meta.user_id)
        )
    except Exception as e:
        return DefaultFailureSchema(message="Failed to create transactions", error=str(e))


@transactions_router.post(Endpoints.api_fetch)
async def fetch_transactions(request_data: FetchCategories, session: Annotated[Session, Depends(get_session)], meta: MetaInfoSchema):
    try:
        t_handler = TransactionHandler(session=session,table=Transactions)
        return DefaultResponseSchema(data=t_handler.fetch_transaction(request_data))
    except Exception as e:
        return DefaultFailureSchema(message="Failed to fetch transactions", error=str(e))
