from datetime import datetime, timezone
from typing import Annotated, Tuple

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.api_key import APIKeyBase
from pydantic import BaseModel, Field

from scripts.config import Services
from scripts.config.constants import Secrets
from scripts.core.db.redis import login_db
from scripts.exceptions.messages import ErrorMessages
from scripts.logging import logger
from scripts.utils.create_token import create_token
from scripts.utils.jwt import JWT


class _MetaInfoSchema(BaseModel):
    user_id: str | None = ""
    login_token: str | None = Field(
        default="",
        validation_alias=Secrets.access_token,
        serialization_alias=Secrets.access_token,
    )


class _CookieAuthentication(APIKeyBase):
    """
    Authentication backend using a cookie.
    Internally, uses a JWT token to store the data.
    """

    def __init__(
        self,
        cookie_name: str = Secrets.access_token,
    ):
        super().__init__()
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.scheme_name = self.__class__.__name__
        self.cookie_name = cookie_name
        self.login_redis = login_db
        self.jwt = JWT()

    def token_validation(
        self, jwt_token: dict, login_token: str, host: str
    ) -> Tuple[str, str]:
        """
        Validates a token for user authorization and refreshes it if necessary.
        Args:
            jwt_token: Dictionary containing JWT tokens.
            login_token: Login token for the user.
            host: Host information for the token validation.
        Returns:
            Tuple[str, str]: User ID extracted from the token.
        Raises:
            HTTPException: If token validation fails or unauthorized access is detected.
        """
        access_token = jwt_token.get("access_token")
        refresh_token = jwt_token.get("refresh_token")
        decoded_token = self.jwt.validate(token=access_token)
        decoded_refresh_token = self.jwt.validate(token=refresh_token)
        if not decoded_token and not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        _token = decoded_token.get("token")
        _age = int(decoded_token.get("age", Secrets.LOCK_OUT_TIME_MINS))
        time_diff = (
            datetime.now(timezone.utc)
            - datetime.fromtimestamp(
                int(jwt_token.get("last_active")) / 1000, tz=timezone.utc
            )
        ).total_seconds() / 60

        if time_diff > Secrets.LOCK_OUT_TIME_MINS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        elif not decoded_refresh_token:
            try:
                new_token = create_token(
                    user_id=decoded_token.get("user_id"),
                    ip=host,
                    token=_token,
                    age=_age,
                    login_token=login_token,
                )
                logger.debug(f"Token : {new_token}")
                return decoded_token.get("user_id")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail=e.args
                ) from e
        login_db.hset(
            login_token,
            mapping={
                "last_active": int(datetime.now(timezone.utc).timestamp() * 1000),
            },
        )
        return decoded_token.get("user_id")

    @staticmethod
    async def update_headers_and_cookies(response: Response, login_token: str) -> None:
        """
        Updates the headers and cookies in the response object with the provided login token.
        Args:
            response: Response object to update.
            login_token: Login token to set as a cookie.
        Returns:
            None
        """
        response.set_cookie(
            Secrets.access_token,
            login_token,
            samesite="strict",
            httponly=True,
            secure=Services.SECURE_ACCESS,
            max_age=Secrets.LOCK_OUT_TIME_MINS * 60,
        )

    async def __call__(self, request: Request, response: Response) -> _MetaInfoSchema:
        """
        Handles the authorization process for incoming requests by validating tokens and updating headers and cookies.
        Args:
            request: Request object for the incoming request.
            response: Response object for the outgoing response.
        Returns:
            _MetaInfoSchema: Metadata schema containing user ID, IP address, and new token information.
        Raises:
            HTTPException: If authorization fails or an unknown error occurs during the process.
        """
        cookies = request.cookies
        login_token = cookies.get(self.cookie_name) or request.headers.get(
            self.cookie_name
        )
        if Services.SECURE_ACCESS:
            if not login_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            jwt_token = self.login_redis.hgetall(login_token)

            if not jwt_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            try:
                user_id = self.token_validation(
                    jwt_token=jwt_token,
                    login_token=login_token,
                    host=request.client.host if request.client else "0.0.0.0",
                )
                await self.update_headers_and_cookies(response, login_token)
            except Exception as e:
                logger.exception(e)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ErrorMessages.UNKNOWN_ERROR,
                ) from e
            logger.debug(login_token)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token doesn't have required fields",
                )
            user_id = user_id
        else:
            user_id = cookies.get("user_id", request.headers.get("user_id"))
        new_token = login_token
        return _MetaInfoSchema(
            user_id=user_id,
            ip_address=request.client.host if request.client else "0.0.0.0",
            new_token=new_token,
        )


CookieAuthentication = _CookieAuthentication()
MetaInfoSchema = Annotated[_MetaInfoSchema, Depends(CookieAuthentication)]

_all_ = ["MetaInfoSchema", "CookieAuthentication"]
