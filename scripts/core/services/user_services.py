from fastapi import APIRouter

from scripts.api import Endpoints
from scripts.core.handlers.user_handler import UserHandler
from scripts.core.schemas import DefaultResponseSchema, DefaultFailureSchema
from scripts.core.schemas.user_model import UserUpdateModel
from scripts.exceptions.module_exception import CustomError
from scripts.utils.authorisation import MetaInfoSchema

user_router = APIRouter(prefix=Endpoints.api_user)


@user_router.post(Endpoints.api_update)
async def update_user_info(request_data: UserUpdateModel, meta: MetaInfoSchema):
    try:
        user_handler = UserHandler()
        return DefaultResponseSchema(
            data=user_handler.update_user_info(
                request_data=request_data, user_id=meta.user_id
            ),
            message=f"Successfully updated the user {meta.user_id}",
        )
    except CustomError as ce:
        return DefaultFailureSchema(message=str(ce), error=str(ce))
    except Exception as e:
        return DefaultFailureSchema(message="Failed to update", error=str(e))
