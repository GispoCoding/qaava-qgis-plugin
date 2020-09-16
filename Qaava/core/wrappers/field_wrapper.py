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

from PyQt5.QtCore import QVariant
from psycopg2 import sql
from psycopg2.sql import Composable
from qgis.core import QgsField

from ...definitions.qui import Settings
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.settings import get_setting


class FieldWrapper:

    def __init__(self, layer_wrapper, field: QgsField, values: Set, pk_name: Optional[str] = None,
                 ) -> None:
        from .layer_wrapper import LayerWrapper
        self.layer_wrapper: LayerWrapper = layer_wrapper
        self.name = field.name()
        self._alias = field.alias()
        self.type = field.type()
        self.unique_values = values
        self.pk_name = pk_name

    @staticmethod
    def from_layer_wrapper(lw, field: QgsField, values: Set,
                           pk_name: str) -> 'FieldWrapper':
        return FieldWrapper(lw, field, values, pk_name)

    @staticmethod
    def is_proper_field(field_name: str, pk_field: Optional[str] = None) -> bool:
        should_not_start_with = get_setting(Settings.field_name_should_not_start_with.name,
                                            Settings.field_name_should_not_start_with.value,
                                            str).split(',')
        if pk_field:
            should_not_start_with.append(pk_field)

        return not any(field_name.lower().startswith(x) for x in should_not_start_with)

    @property
    def has_parent(self) -> bool:
        return (self.layer_wrapper.parent_layer is not None) and not self.is_many_to_many

    @property
    def is_many_to_many(self) -> bool:
        return False

    @property
    def table(self) -> Composable:
        uri = self.layer_wrapper.uri
        return sql.Identifier(uri.schema(), uri.table())

    @property
    def field(self) -> Composable:
        uri = self.layer_wrapper.uri
        return sql.Identifier(uri.table(), self.name)

    @property
    def field_with_table(self) -> str:
        uri = self.layer_wrapper.uri
        return '_'.join((uri.schema(), uri.table(), self.name))

    @property
    def pk(self) -> Composable:
        uri = self.layer_wrapper.uri
        return sql.Identifier(uri.schema(), uri.table(), self.pk_name)

    @property
    def fk(self) -> Composable:
        return self.layer_wrapper.foreign_field.field

    @property
    def alias(self) -> str:
        alias = self._alias if self._alias != '' else self.name
        if self.has_parent or self.is_many_to_many:
            return f'{self.layer_wrapper.layer_name}.{alias}'
        else:
            return alias

    def get_field(self):
        return [f for f in self.layer_wrapper.get_layer().fields().toList() if f.name() == self.name][0]

    def __str__(self) -> str:
        return f'{self.alias} ({self.name})'


class IsForeignNullFieldWrapper(FieldWrapper):

    def __init__(self, layer_wrapper, field: QgsField, values: Set, pk_name: str, other_layer_name: str,
                 f_pk: Optional[FieldWrapper] = None) -> None:
        super().__init__(layer_wrapper, field, values, pk_name)
        self.type = QVariant.Bool
        self.other_layer_name = other_layer_name
        self.f_pk: Optional[FieldWrapper] = f_pk

    @staticmethod
    def create(lw, field: QgsField, values: Set, pk_name: str, other_layer_name: str,
               f_pk: Optional[FieldWrapper] = None):
        return IsForeignNullFieldWrapper(lw, field, values, pk_name, other_layer_name, f_pk)

    @property
    def pk(self) -> Composable:
        if self.f_pk is None:
            return super().pk
        else:
            return self.f_pk.field

    @property
    def alias(self) -> str:
        return tr('Has {}', self.other_layer_name)


class RelationalFieldWrapper(FieldWrapper):

    def __init__(self, rel_layer_wrapper, layer_wrapper, field: QgsField, values: Set) -> None:
        from .layer_wrapper import RelationalLayerWrapper
        super().__init__(layer_wrapper, field, values)

        self.rel_layer_wrapper: RelationalLayerWrapper = rel_layer_wrapper

    @staticmethod
    def from_relation_wrapper(rlw, lw, field: QgsField,
                              values: set) -> 'RelationalFieldWrapper':
        return RelationalFieldWrapper(rlw, lw, field, values)

    @property
    def is_many_to_many(self) -> bool:
        return True

    @property
    def many_to_many_table(self) -> Composable:
        uri = self.rel_layer_wrapper.uri
        return sql.Identifier(uri.schema(), uri.table())

    @property
    def m_a(self) -> Composable:
        return self.rel_layer_wrapper.fw_m_a.field

    @property
    def a_pk(self) -> Composable:
        return self.rel_layer_wrapper.fw_a.field

    @property
    def m_b(self) -> Composable:
        return self.rel_layer_wrapper.fw_m_b.field

    @property
    def b_pk(self) -> Composable:
        return self.rel_layer_wrapper.fw_b.field
