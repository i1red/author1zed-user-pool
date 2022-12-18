from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from author1zd.database.abstract.repositories.user_repository import UserRepository
from author1zd.database.exceptions import NonUniqueUserDataException
from author1zd.database.sqlalchemy.models import UserModel
from author1zd.database.sqlalchemy.converters.converter import Converter
from author1zd.database.sqlalchemy.converters.default_converter import DefaultConverter
from author1zd.entities.user import User


class SqlAlchemyUserRepository(UserRepository):
    def __init__(
        self, session: Session, converter: Converter[User, UserModel] = DefaultConverter(User, UserModel)
    ) -> None:
        self._session = session
        self._converter = converter

    def save(self, user_entity: User) -> User:
        try:
            with self._session:
                user_model = self._converter.entity_to_model(user_entity)
                self._session.add(user_model)
                self._session.commit()

                self._session.refresh(user_model)
                return self._converter.model_to_entity(user_model)
        except IntegrityError:
            raise NonUniqueUserDataException("Username and email should be unique")

    def get_by_username(self, username: str) -> User | None:
        with self._session:
            user_model = self._session.query(UserModel).filter(UserModel.username == username).first()
            if user_model is None:
                return None
            return self._converter.model_to_entity(user_model)

    def get_by_id(self, user_id: int) -> User | None:
        with self._session:
            user_model = self._session.get(UserModel, user_id)
            if user_model is None:
                return None
            return self._converter.model_to_entity(user_model)
