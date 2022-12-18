from abc import ABC, abstractmethod

from entities.client import Client


class ClientRepository(ABC):
    # NOTE: Authorization Server API does NOT include client registration,
    # client should be registered separately
    # Therefore ClientRepository does NOT provide methods to save client

    @abstractmethod
    def get_by_client_id(self, client_id: str) -> Client | None:
        """Get client by client_id"""
