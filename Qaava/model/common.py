import enum
import sys

from PyQt5.QtCore import QVariant
from psycopg2 import sql

if sys.version_info >= (3, 8):
    from typing import Type, TypedDict, Optional
else:
    from typing import Type
    from typing_extensions import TypedDict


class Schema(enum.Enum):
    CODES = 'koodistot'


class DatabaseTable:
    schema = ''
    _table = ''
    gid = sql.Identifier('gid')

    class Type(TypedDict):
        gid: int

    @classmethod
    def table(cls):
        return sql.Identifier(cls.schema, cls._table)


class DatabaseField:

    def __init__(self, name: str, field_type: Optional[QVariant] = None, table: Optional[str] = None):
        self.field = sql.Identifier(name)
        self.type = field_type
        self.table = table

    def __str__(self):
        return self.field.string if self.table is None else f"{self.table}.{self.field.string}"


class DbRelation:

    def __init__(self, table: Type[DatabaseTable], relation_id: str):
        self.table = table
        self.rel_id = relation_id

    @property
    def field(self):
        return sql.Identifier(self.rel_id)


class ProcessInfo(DatabaseTable):
    schema = Schema.CODES.value
    _table = 'vaihetieto'
    name = DatabaseField('nimi', table='vaihetieto')

    class Type(DatabaseTable.Type):
        name: str
