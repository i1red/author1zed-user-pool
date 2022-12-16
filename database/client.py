from database.models import ClientAppModel
from database.session import Session


class ClientNotRegisteredException(Exception):
    pass


class RedirectUriNotAllowedException(Exception):
    pass


def check_redirect_uri(client_id: str, redirect_uri: str) -> None:
    with Session() as session:
        client_app = (
            session.query(ClientAppModel)
            .filter(ClientAppModel.client_id == client_id)
            .first()
        )

        if client_app is None:
            raise ClientNotRegisteredException(
                "Client app with provided 'client_id' not found"
            )

        allowed_redirect_uris = [
            redirect_uri.uri for redirect_uri in client_app.redirect_uris
        ]

        if redirect_uri not in allowed_redirect_uris:
            raise RedirectUriNotAllowedException(
                "Provided 'redirect_uri' is not allowed for client"
            )
