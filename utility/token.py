import datetime

from jose import jwt

from database.models import UserModel
from key_value_storage.redis.collections.redis_string_set import RedisStringSet
from settings import JwtSettings


def generate_token_pair(
    client_id: str, user: UserModel, refresh_token_collection: RedisStringSet, jwt_settings: JwtSettings
) -> dict:
    access_token_claims = {
        "client_id": client_id,
        "email": user.email,
        "username": user.username,
        "sub": str(user.id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=jwt_settings.access_token_ttl),
    }
    access_token = jwt.encode(
        access_token_claims,
        key=jwt_settings.access_token_secret_key,
        algorithm=jwt_settings.algorithm,
    )

    refresh_token_claims = {
        "client_id": client_id,
        "sub": str(user.id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=jwt_settings.refresh_token_ttl),
    }
    refresh_token = jwt.encode(
        refresh_token_claims,
        key=jwt_settings.refresh_token_secret_key,
        algorithm=jwt_settings.algorithm,
    )
    refresh_token_collection.save(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires_in": jwt_settings.access_token_ttl,
        "refresh_token_expires_in": jwt_settings.refresh_token_ttl,
        "token_type": "Bearer",
    }
