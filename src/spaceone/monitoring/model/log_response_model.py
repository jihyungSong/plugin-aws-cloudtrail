from schematics.models import Model
from schematics.types import BaseType, ListType, DictType, StringType, UnionType, IntType, FloatType
from schematics.types.compound import ModelType

__all__ = ['LogResponseModel']


class LogModel(Model):
    logs = ListType(DictType(StringType))


class LogResponseModel(Model):
    resource_type = StringType(required=True, default='monitoring.Log')
    actions = ListType(DictType(StringType))
    result = ModelType(LogModel)
