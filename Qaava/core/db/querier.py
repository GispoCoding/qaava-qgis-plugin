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
from typing import Optional, Dict, List, Tuple

from PyQt5.QtCore import QVariant
from qgis.core import QgsRectangle

from .db_utils import get_db_connection_params
from .query_repository import QueryRepository
from ..wrappers.field_wrapper import FieldWrapper
from ...definitions.db import Operation
from ...model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class Querier:
    """
    Abstraction of query_repository for query_panel
    """

    def __init__(self, plan_enum_str: str, limit_for_unique: int = 0):
        self.plan_enum = LandUsePlanEnum[plan_enum_str]
        self.plan: Optional[LandUsePlan] = None
        self.limit_for_unique = limit_for_unique
        self.qr: Optional[QueryRepository] = None
        self._fields: Dict[str, FieldWrapper] = {}
        self._initialize()

    def _initialize(self):
        self.plan: LandUsePlan = self.plan_enum.value
        conn_params = get_db_connection_params(self.plan_enum)
        self.qr = QueryRepository(conn_params, self.plan_enum)

        fields = self.plan.layer.get_fields(self.limit_for_unique)
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

    def run(self) -> List[int]:
        """
        Run the current query
        :return: Gid numbers of matching rows
        """
        return self.qr.run_query()

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

    def add_condition(self, field: FieldWrapper, operation: Operation, value: str):
        """
        Add condition for the query

        :param field: Database field
        :param operation: Operation
        :param value: value as string
        :return:
        """
        val = None if not len(value) or value.lower() in ['null', 'none', 'tyhjä'] else value
        if val is None:
            operation = Operation.IS
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
            rnd(extent.yMaximum())
        )
