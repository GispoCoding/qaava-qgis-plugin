import enum
from typing import TypedDict, Type

from psycopg2 import sql


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


class DbRelation:

    def __init__(self, table: Type[DatabaseTable], relation_id: str):
        self.table = table
        self.rel_id = relation_id

    @property
    def id(self):
        return sql.Identifier(self.rel_id)


class ProcessInfo(DatabaseTable):
    schema = Schema.CODES.value
    _table = 'vaihetieto'
    name = sql.Identifier('nimi')

    class Type(DatabaseTable.Type):
        name: str
