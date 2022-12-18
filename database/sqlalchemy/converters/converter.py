from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from database.sqlalchemy.models import BaseModel


TEntity = TypeVar("TEntity")
TModel = TypeVar("TModel", bound=BaseModel)


class Converter(ABC, Generic[TEntity, TModel]):
    @abstractmethod
    def entity_to_model(self, entity: TEntity) -> TModel:
        """Covert business entity to database model"""

    @abstractmethod
    def model_to_entity(self, model: TModel) -> TEntity:
        """Convert database model to business entity"""
