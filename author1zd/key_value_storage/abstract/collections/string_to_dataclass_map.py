from abc import ABC, abstractmethod
from typing import Generic, TypeVar


TObject = TypeVar("TObject")


class StringToDataclassMap(ABC, Generic[TObject]):
    @abstractmethod
    def save(self, key: str, obj: TObject) -> None:
        """Save key:object pair to map"""

    @abstractmethod
    def get(self, key: str) -> TObject | None:
        """Get object by key"""

    @abstractmethod
    def remove(self, key: str) -> None:
        """Remove key:object pair from map"""
