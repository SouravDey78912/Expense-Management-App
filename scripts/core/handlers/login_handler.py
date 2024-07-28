import bcrypt
import shortuuid
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from scripts.config.constants import Secrets
from scripts.core.db.mongo import mongo_client
from scripts.core.db.mongo.expense_tracker.user import UserMongo
from scripts.core.db.redis import login_db
from scripts.core.schemas.auth_model import UserModel, LoginModel
from scripts.logging import logger
from scripts.utils.create_token import create_token
from scripts.utils.jwt import JWT


class LoginHandler:
    def __init__(self):
        self.users_collection = UserMongo(mongo_client=mongo_client)
        self.jwt = JWT()

    def create_user(self, user: UserModel) -> str:
        """
        Creates a new user using the provided UserModel object.
        Args:
            user: UserModel object containing user details.
        Returns:
            str: ID of the created user.
        Raises:
            HTTPException: If the username or email already exists in the database.
        """

        if self.users_collection.find_one(
            {"$or": [{"username": user.username}, {"email": user.email}]}
        ):
            raise HTTPException(
                status_code=400, detail="Username or email already exists"
            )

        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        user_id = f"user_{str(shortuuid.uuid())}"
        user.user_id = user_id
        user.password = hashed_password
        self.users_collection.insert_one(user.model_dump())
        return user_id

    def authenticate_user(
        self, request: Request, response: Response, request_data: LoginModel
    ):
        """
        Authenticates a user based on the provided login data.
        Args:
            request: Request object.
            response: Response object.
            request_data: LoginModel object containing login details.
        Returns:
            None
        Raises:
            HTTPException: If authentication fails due to invalid username or password.
            Any other Exception raised during the authentication process.
        """

        try:
            self._perform_authentication(request_data, request, response)
        except HTTPException as He:
            logger.info(f"Failed to login Invalid username or password: {str(He)}")
            raise
        except Exception as e:
            logger.info(f"Failed to login : {str(e)}")
            raise

    def _perform_authentication(self, request_data, request, response):
        """
        Performs user authentication based on the provided request data.
        Args:
            request_data: Data containing the username and password for authentication.
            request: Request object.
            response: Response object.
        Returns:
            None
        Raises:
            HTTPException: If the username or password is invalid during authentication.
        """
        try:
            user = self.users_collection.find_one({"username": request_data.username})
            if not user or not bcrypt.checkpw(
                request_data.password.encode("utf-8"), user["password"]
            ):
                raise HTTPException(
                    status_code=400, detail="Invalid username or password"
                )

            if user.get("token_id") and login_db.hgetall(user.get("token_id")):
                logger.debug("UUID exists continuing with the same for login.")
            else:
                user["token_id"] = ""
            _uuid = create_token(
                user_id=user["user_id"],
                ip=request.client.host if request.client else "0.0.0.0",
                token=self.jwt.encode(
                    payload={"user_id": user["user_id"], "email": user["email"]}
                ),
                login_token=user["token_id"],
            )
            self.users_collection.update_one(
                query={"user_id": user["user_id"]}, data={"token_id": _uuid}
            )
            response.headers[Secrets.access_token] = _uuid
        except Exception as e:
            logger.info(f"Failed to validate : {str(e)}")
            raise

    def logout(self, user_id):
        """
        Logs out a user by deleting their token from the login database.
        Args:
            user_id: ID of the user to logout.
        Returns:
            None
        Raises:
            Any Exception raised during the logout process.
        """
        try:
            user_token = self.users_collection.find_one(
                {"user_id": user_id}, filter_dict={"_id": 0, "token_id": 1}
            )
            login_db.delete(user_token.get("token_id", ""))
        except Exception as e:
            logger.info(f"Failed to logout : {str(e)}")
            raise
