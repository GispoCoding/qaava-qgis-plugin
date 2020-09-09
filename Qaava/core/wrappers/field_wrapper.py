#  Gispo Ltd., hereby disclaims all copyright interest in the program Qaava-qgis-plugin
#  Copyright (C) 2020 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Qaava-qgis-plugin.
#
#  Qaava-qgis-plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Qaava-qgis-plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Qaava-qgis-plugin.  If not, see <https://www.gnu.org/licenses/>.
from typing import Set, Optional

from psycopg2 import sql
from psycopg2.sql import Composable
from qgis.core import QgsField


class FieldWrapper:

    def __init__(self, field: QgsField, idx: int, values: Set, layer_name: str, schema: str, table: str,
                 parent_layer_name: Optional[str] = None,
                 parent_table: Optional[str] = None,
                 pk_name: Optional[str] = None,
                 foreign_field: Optional['FieldWrapper'] = None) -> None:
        self.name = field.name()
        self._alias = field.alias()
        self.type = field.type()
        self.layer_name = layer_name
        self.idx = idx
        self.unique_values = values
        self.schema = schema
        self._table = table
        self.parent_layer_name = parent_layer_name
        self.parent_table = parent_table
        self.pk_name = pk_name
        self.foreign_field = foreign_field

    @staticmethod
    def from_layer_wrapper(lw, field: QgsField, idx: int, values: Set,
                           pk_name: str) -> 'FieldWrapper':
        from .layer_wrapper import LayerWrapper
        lw: LayerWrapper = lw
        uri = lw.uri
        table = uri.table()
        schema = uri.schema()
        if lw.parent_layer is not None:
            par_layer: LayerWrapper = lw.parent_layer
            uri = par_layer.uri
            return FieldWrapper(field, idx, values, lw.layer_name, schema=schema, table=table,
                                parent_layer_name=par_layer.layer_name, parent_table=uri.table(),
                                pk_name=pk_name, foreign_field=lw.foreign_field)
        else:
            return FieldWrapper(field, idx, values, lw.layer_name, schema=schema, table=table,
                                pk_name=pk_name)

    @property
    def has_parent(self) -> bool:
        return self.parent_layer_name is not None

    @property
    def table(self) -> Composable:
        return sql.Identifier(self.schema, self._table)

    @property
    def field(self) -> Composable:
        if self.has_parent:
            return sql.Identifier(self.schema, self._table, self.name)
        else:
            return sql.Identifier(self.name)

    @property
    def field_with_table(self) -> str:
        return '_'.join((self.schema, self._table, self.name))

    @property
    def pk(self) -> Composable:
        return sql.Identifier(self.schema, self._table, self.pk_name)

    @property
    def fk(self) -> Composable:
        return self.foreign_field.field

    @property
    def alias(self) -> str:
        alias = self._alias if self._alias != '' else self.name
        if self.has_parent:
            return f'{self.layer_name}.{alias}'
        else:
            return alias

    def __str__(self) -> str:
        return f'{self.alias} ({self.name})'
