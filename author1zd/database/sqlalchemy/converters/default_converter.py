from dataclasses import asdict
from typing import Type, TypeVar

from author1zd.database.sqlalchemy.models import BaseModel
from author1zd.database.sqlalchemy.converters.converter import Converter

TEntity = TypeVar("TEntity")
TModel = TypeVar("TModel", bound=BaseModel)


class DefaultConverter(Converter[TEntity, TModel]):
    def __init__(self, entity_type: Type[TEntity], model_type: Type[TModel]) -> None:
        self._entity_type = entity_type
        self._model_type = model_type

    def entity_to_model(self, entity: TEntity) -> TModel:
        model = self._model_type()

        for field, value in asdict(entity).items():
            if value is not None:
                setattr(model, field, value)

        return model

    def model_to_entity(self, model: TModel) -> TEntity:
        entity_kwargs = {}

        for column in model.__table__.columns:
            entity_kwargs[column.name] = getattr(model, column.name)

        return self._entity_type(**entity_kwargs)
