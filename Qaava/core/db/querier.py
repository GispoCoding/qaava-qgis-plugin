#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from typing import Optional, Dict, List, Tuple, Union

from PyQt5.QtCore import QVariant
from qgis.core import QgsRectangle, QgsVectorLayer

from .db_utils import get_db_connection_params
from .query_repository import QueryRepository
from ..wrappers.field_wrapper import FieldWrapper, IsForeignNullFieldWrapper
from ..wrappers.layer_wrapper import LayerWrapper
from ...definitions.db import Operation
from ...model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class Querier:
    """
    Abstraction of query_repository for query_panel
    """

    def __init__(self, plan_enum_str: str, layer: QgsVectorLayer, limit_for_unique: int = 0):
        self.plan_enum = LandUsePlanEnum[plan_enum_str]
        self.plan: LandUsePlan = self.plan_enum.value
        self.layer_wrapper = LayerWrapper.from_qgs_layer(layer)
        self.limit_for_unique = limit_for_unique
        self.qr: Optional[QueryRepository] = None
        self._fields: Dict[str, FieldWrapper] = {}
        self._initialize()

    def _initialize(self):
        conn_params = get_db_connection_params(self.plan_enum)
        self.qr = QueryRepository(conn_params, self.plan_enum, self.layer_wrapper)

        fields = self.layer_wrapper.get_fields(self.limit_for_unique)
        self._fields = {f.alias: f for f in fields}

    @property
    def fields(self) -> Dict[str, FieldWrapper]:
        """
        Database fields available for queries
        :return:
        """
        return self._fields

    def clear(self):
        """
        Clear query
        """
        self.qr.clear()

    def run(self) -> List[Union[int, str]]:
        """
        Run the current query
        :return: Gid numbers of matching rows
        """
        return self.qr.run_query()

    def set_filter(self, ids: List[int]) -> bool:
        """
        Set filter for the layer
        :param ids: ids that will are shown
        :return: Whether filtering was successful
        """
        return self.layer_wrapper.set_filter(ids)

    def clear_filter(self) -> bool:
        """
        Clear filter from the layer
        :return: Whether clearing was successful
        """
        return self.layer_wrapper.clear_filter()

    def show_query(self) -> str:
        """
        Shows the generated query text
        :return:
        """
        return self.qr.show_query()

    def fetch_choices(self, field: FieldWrapper) -> Tuple[List, bool]:
        """
        Fetch choices for the field if any

        :param field: FieldWrapper
        :return: Choice list and whether choices are string or not
        """
        null = QVariant()
        unique_values = [val for val in field.unique_values if val != null]
        return unique_values, field.type == QVariant.String

    def add_condition(self, field: FieldWrapper, operation: Operation, value: Union[str, bool]):
        """
        Add condition for the query

        :param field: FieldWrapper
        :param operation: Operation
        :param value: value as string or boolean
        :return:
        """
        val = value
        if isinstance(value, str):
            val = None if not len(value) or value.lower() in ['null', 'none', 'tyhjä'] else value
            if val is None:
                operation = Operation.IS if operation != Operation.IS_NOT else Operation.IS_NOT
            else:
                if field.type in [
                    QVariant.Int,
                    QVariant.UInt,
                    QVariant.LongLong,
                    QVariant.ULongLong
                ]:
                    val = int(val)
                elif field.type == QVariant.Double:
                    val = float(val)
        if isinstance(field, IsForeignNullFieldWrapper):
            operation = Operation.IS_NOT if value else Operation.IS
            val = None

        return self.qr.add_and_condition(field, operation, val)

    def add_extent(self, extent: QgsRectangle, precision=4):
        """
        Add extent for the query

        :param extent: QgsRectangle expected to be in the right extent
        :param precision: Precision of coordinates
        :return:
        """
        rnd = lambda c: round(c, precision)
        self.qr.add_extent(
            rnd(extent.xMinimum()),
            rnd(extent.yMinimum()),
            rnd(extent.xMaximum()),
            rnd(extent.yMaximum()),
            srid=self.layer_wrapper.get_layer().crs().srsid()
        )
