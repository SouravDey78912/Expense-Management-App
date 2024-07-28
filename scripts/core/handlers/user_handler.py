import shortuuid

from scripts.core.db.mongo import mongo_client
from scripts.core.db.mongo.expense_tracker.user import UserMongo
from scripts.core.schemas.user_model import UserUpdateModel
from scripts.exceptions.module_exception import CustomError
from scripts.logging import logger


class UserHandler():
    def __init__(self):
        self.users_collection = UserMongo(mongo_client=mongo_client)

    def update_user_info(self, request_data: UserUpdateModel, user_id):
        """
        Updates user information based on the provided UserUpdateModel object.
        Args:
            request_data: UserUpdateModel object containing updated user details.
            user_id: ID of the user to update.
        Returns:
            None
        Raises:
            CustomError: If the user is unknown or any other Exception occurs during the update process.
        """
        try:
            if self.users_collection.find_one(
                {
                    "username": request_data.username,
                    "user_id": {"$ne": request_data.user_id},
                },
                filter_dict={"_id": 0, "user_id": 1},
            ):
                raise CustomError("Username already exists!!")

            if self.users_collection.find_one(
                {"user_id": user_id}, filter_dict={"_id": 0, "user_id": 1}
            ):
                self.users_collection.update_one(
                    query={"user_id": user_id}, data=request_data.model_dump()
                )
                return
            raise CustomError("Unknown User !!")
        except Exception as e:
            logger.info(f"Failed to update user info : {str(e)}")
            raise
