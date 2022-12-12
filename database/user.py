import sqlalchemy.exc
from sqlalchemy.orm import Session

from database.engine import ENGINE
from database.models import UserModel


class NonUniqueUserDataException(Exception):
    pass


def save_user(username: str, email: str, password_hash: str) -> None:
    try:
        with Session(ENGINE) as session:
            user = UserModel(username=username, email=email, password_hash=password_hash)
            session.add(user)
            session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise NonUniqueUserDataException("Username and email should be unique")
