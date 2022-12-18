from abc import ABC, abstractmethod

from entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        """Save user to database"""

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Get user by username"""

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by id"""
