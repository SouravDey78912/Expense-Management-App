import uuid
from datetime import datetime, timezone, timedelta

from scripts.config.constants import Secrets
from scripts.core.db.redis import login_db
from scripts.exceptions.module_exception import CustomError
from scripts.utils.jwt import JWT


def create_token(
    user_id,
    ip,
    token,
    age=Secrets.LOCK_OUT_TIME_MINS,
    login_token=None,
):
    """
    This method is to create a cookie
    """
    try:
        jwt = JWT()
        uid = login_token or str(uuid.uuid4()).replace("-", "")

        access_payload = {
            "ip": ip,
            "user_id": user_id,
            "token": token,
            "uid": uid,
            "age": age,
        }
        exp = datetime.now(timezone.utc) + timedelta(minutes=age)
        _extras = {"exp": exp}
        _payload = access_payload | _extras
        access_token = jwt.encode(_payload)
        refresh_token_payload = {
            "ip": ip,
            "user_id": user_id,
            "token": token,
            "uid": uid,
            "age": Secrets.REFRESH_TIME_IN_MINS,
        }
        exp = datetime.now(timezone.utc) + timedelta(
            minutes=Secrets.REFRESH_TIME_IN_MINS
        )
        _extras = {"exp": exp}
        _payload = refresh_token_payload | _extras
        refresh_token = jwt.encode(_payload)

        login_db.hset(
            uid,
            mapping={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "last_active": int(datetime.now(timezone.utc).timestamp() * 1000),
            },
        )
        login_db.expire(
            uid,
            timedelta(
                minutes=(Secrets.REFRESH_TIME_IN_MINS + age + Secrets.LEEWAY_IN_MINS)
            ),
        )

        return uid
    except Exception as e:
        raise CustomError(f"{str(e)}") from e
