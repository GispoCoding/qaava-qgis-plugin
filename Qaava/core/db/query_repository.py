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

import logging
from typing import List, Dict, Optional, Union

from psycopg2.sql import SQL, Composable

from .database import Database
from ..wrappers.field_wrapper import FieldWrapper
from ..wrappers.layer_wrapper import LayerWrapper
from ...definitions.db import Operation
from ...model.land_use_plan import LandUsePlanEnum
from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


# noinspection PyUnresolvedReferences
class QueryRepository(Database):

    def __init__(self, conn_params: Dict[str, str], plan_enum: LandUsePlanEnum,
                 layer_wrapper: Optional[LayerWrapper] = None):
        super().__init__(conn_params)
        self.plan_enum = plan_enum
        self.select_parts: List[Composable] = []
        self.from_parts: List[Composable] = []
        self.where_parts: List[Composable] = []
        self.vars: Dict[str, any] = {}
        self.layer_wrapper = layer_wrapper if layer_wrapper is not None else self.plan_enum.value.layer

        self._set_initial_parts()

    @property
    def query(self) -> Composable:
        return self.reduce_query(self.select_parts, self.from_parts, self.reduce_where_parts(self.where_parts))

    def clear(self):
        self.select_parts.clear()
        self.from_parts.clear()
        self.where_parts.clear()
        self.vars.clear()
        self._set_initial_parts()

    def add_and_condition(self, field: FieldWrapper, operation: Operation, value: any) -> None:
        if field.has_parent:
            self.from_parts.append(
                SQL('LEFT JOIN {f_table} ON {gid_f}={f_pk}').format(f_table=field.table, gid_f=field.fk, f_pk=field.pk)
            )

        self.where_parts.append(
            SQL('{fld}' + operation.value + '%(' + field.field_with_table + ')s').format(fld=field.field)
        )

        self.vars[field.field_with_table] = value

    def add_extent(self, xmin: float, ymin: float, xmax: float, ymax: float, srid=3877) -> None:
        self.where_parts.append(
            SQL('{geom} && ST_MakeEnvelope(%(xmin)s, %(ymin)s, %(xmax)s, %(ymax)s, %(srid)s)').format(
                geom=self.layer_wrapper.geom_field)
        )
        self.vars.update({'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax, 'srid': srid})

    def run_query(self) -> List[Union[int, str]]:
        return [row[0] for row in self.execute_select(self.query, self.vars)]

    def show_query(self) -> str:
        return self.mogrify_query(self.query, self.vars)

    def _set_initial_parts(self):
        self.select_parts.append(SQL('SELECT {pk}').format(pk=self.layer_wrapper.pk))
        self.from_parts.append(SQL('FROM {table}').format(table=self.layer_wrapper.table))
