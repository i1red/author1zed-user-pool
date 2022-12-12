import sqlalchemy.exc

from database.engine import ENGINE
from database.models import users


class NonUniqueUserDataException(Exception):
    pass


def save_user(username: str, email: str, password_hash: str) -> None:
    try:
        with ENGINE.connect() as connection:
            query = users.insert().values(username=username, email=email, password_hash=password_hash)
            connection.execute(query)
    except sqlalchemy.exc.IntegrityError:
        raise NonUniqueUserDataException("Username and password should be unique")
