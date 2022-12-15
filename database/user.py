from typing import Optional

import sqlalchemy.exc

from database.session import Session
from database.models import UserModel


class NonUniqueUserDataException(Exception):
    pass


def save_user(username: str, email: str, password_hash: str) -> None:
    try:
        with Session() as session:
            user = UserModel(username=username, email=email, password_hash=password_hash)
            session.add(user)
            session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise NonUniqueUserDataException("Username and email should be unique")


def get_user_by_username(username: str) -> Optional[UserModel]:
    with Session() as session:
        return session.query(UserModel).filter(UserModel.username == username).first()