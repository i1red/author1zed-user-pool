from database.abstract.repositories.client_repository import ClientRepository


class ClientNotRegisteredException(Exception):
    pass


class RedirectUriNotAllowedException(Exception):
    pass


class SecretMismatchException(Exception):
    pass


def check_redirect_uri(client_id: str, redirect_uri: str, client_repository: ClientRepository) -> None:
    client = client_repository.get_by_client_id(client_id)

    if client is None:
        raise ClientNotRegisteredException("Client app with provided 'client_id' not found")

    if redirect_uri not in client.redirect_uris:
        raise RedirectUriNotAllowedException("Provided 'redirect_uri' is not allowed for client")


def check_client_secret(client_id: str, client_secret: str, client_repository: ClientRepository) -> None:
    client = client_repository.get_by_client_id(client_id)

    if client is None:
        raise ClientNotRegisteredException("Client app with provided 'client_id' not found")

    if client.client_secret != client_secret:
        raise SecretMismatchException("Provided client secret does not match")
