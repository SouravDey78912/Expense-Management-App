from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from scripts.api import Endpoints
from scripts.core.handlers.login_handler import LoginHandler
from scripts.core.schemas import DefaultResponseSchema, DefaultFailureSchema
from scripts.core.schemas.auth_model import UserModel, LoginModel
from scripts.utils.authorisation import MetaInfoSchema

login_router = APIRouter(prefix=Endpoints.api_auth)


@login_router.post(Endpoints.api_sign_up)
async def sign_up(user: UserModel):
    try:
        login_handler = LoginHandler()
        return DefaultResponseSchema(data=login_handler.create_user(user))
    except Exception as e:
        return DefaultFailureSchema(message="Failed to signup", error=str(e))


@login_router.post(Endpoints.api_login)
async def login(request_data: LoginModel, request: Request, response: Response):
    try:
        login_handler = LoginHandler()
        return DefaultResponseSchema(
            data=login_handler.authenticate_user(
                request=request, response=response, request_data=request_data
            ),
            message=f"Successfully logged in as {request_data.username}",
        )
    except Exception as e:
        return DefaultFailureSchema(message="Failed to login", error=str(e))


@login_router.post(Endpoints.api_logout)
async def logout(meta: MetaInfoSchema):
    try:
        login_handler = LoginHandler()
        return DefaultResponseSchema(
            data=login_handler.logout(user_id=meta.user_id),
            message="Successfully logged out",
        )
    except Exception as e:
        return DefaultFailureSchema(message="Failed to logout", error=str(e))
