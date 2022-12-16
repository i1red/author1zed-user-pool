import datetime

from jose import jwt

from database.models import UserModel
from redis_data.refresh_token import save_refresh_token
from settings import JwtSettings


def generate_token_pair(
    client_id: str, user: UserModel, jwt_settings: JwtSettings = JwtSettings()
) -> dict:
    access_token_claims = {
        "client_id": client_id,
        "email": user.email,
        "username": user.username,
        "sub": str(user.id),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=jwt_settings.access_token_lifetime),
    }
    access_token = jwt.encode(
        access_token_claims,
        key=jwt_settings.access_token_secret_key,
        algorithm=jwt_settings.algorithm,
    )

    refresh_token_claims = {
        "client_id": client_id,
        "sub": str(user.id),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=jwt_settings.refresh_token_lifetime),
    }
    refresh_token = jwt.encode(
        refresh_token_claims,
        key=jwt_settings.refresh_token_secret_key,
        algorithm=jwt_settings.algorithm,
    )
    save_refresh_token(refresh_token, ttl=jwt_settings.refresh_token_lifetime)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires_in": jwt_settings.access_token_lifetime,
        "refresh_token_expires_in": jwt_settings.refresh_token_lifetime,
        "token_type": "Bearer",
    }
