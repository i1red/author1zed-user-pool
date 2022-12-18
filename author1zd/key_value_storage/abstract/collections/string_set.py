from abc import ABC, abstractmethod


class StringSet(ABC):
    @abstractmethod
    def save(self, key: str) -> None:
        """Save key to set"""

    @abstractmethod
    def contains(self, key: str) -> bool:
        """Check if set contains key"""

    @abstractmethod
    def remove(self, key: str) -> None:
        """Remove key from set"""
