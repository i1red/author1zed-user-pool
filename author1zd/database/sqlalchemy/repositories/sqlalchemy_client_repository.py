from sqlalchemy.orm import Session

from author1zd.database.abstract.repositories.client_repository import ClientRepository
from author1zd.database.sqlalchemy.models import ClientAppModel
from author1zd.entities.client import Client


class SqlAlchemyClientRepository(ClientRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_client_id(self, client_id: str) -> Client | None:
        with self._session:
            client_model = self._session.query(ClientAppModel).filter(ClientAppModel.client_id == client_id).first()
            return Client(
                id=client_model.id,
                client_id=client_model.client_id,
                client_secret=client_model.client_secret,
                redirect_uris=[redirect_uri_model.uri for redirect_uri_model in client_model.redirect_uris],
            )
