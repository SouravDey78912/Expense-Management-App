import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    MissingRequiredClaimError,
)

from scripts.config.constants import Secrets
from scripts.exceptions.messages import ErrorMessages
from scripts.exceptions.module_exception import AuthenticationError
from scripts.logging import logger


class JWT:
    def __init__(self) -> None:
        self.alg: str = Secrets.ALG

    def encode(self, payload) -> str:
        try:
            key = Secrets.KEY
            return jwt.encode(payload, key, algorithm=self.alg)
        except Exception as e:
            logger.exception(f"Exception while encoding JWT: {str(e)}")
            raise

    def decode(self, token):
        try:
            key = Secrets.KEY
            return jwt.decode(token, key, algorithms=self.alg)
        except Exception as e:
            logger.exception(f"Exception while decoding JWT: {str(e)}")
            raise

    def validate(self, token):
        try:
            key = Secrets.KEY
            return jwt.decode(
                token,
                key,
                algorithms=self.alg,
                leeway=Secrets.LEEWAY_IN_MINS,
                options={"require": ["exp"]},
            )
        except InvalidSignatureError as e:
            raise AuthenticationError(ErrorMessages.ERROR003) from e
        except ExpiredSignatureError as e:
            raise AuthenticationError(ErrorMessages.ERROR002) from e
        except MissingRequiredClaimError as e:
            raise AuthenticationError(ErrorMessages.ERROR003) from e
        except Exception as e:
            logger.exception(f"Exception while validating JWT: {str(e)}")
            raise AuthenticationError(ErrorMessages.UNKNOWN_ERROR) from e
