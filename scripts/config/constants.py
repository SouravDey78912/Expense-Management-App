class DBMapping:
    expense_manager = "expense_tracker"


class CollectionMap:
    user = "user"


class Secrets:
    LEEWAY_IN_MINS: int = 10
    ALG = "HS256"
    LOCK_OUT_TIME_MINS: int = 30
    REFRESH_TIME_IN_MINS: int = 60
    KEY = "9-kTElQo1KpR0dlhX0ihY-fBHjf1VcxoindVn7isKo8"
    access_token = "access-token"


class QueryConstants:
    key_column_map = {"created_at": "meta.created_at"}
