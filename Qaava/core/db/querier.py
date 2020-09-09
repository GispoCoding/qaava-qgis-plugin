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

from qgis.core import QgsRectangle

from .db_utils import get_db_connection_params
from .query_repository import QueryRepository
from ...definitions.db import Operation
from ...model.common import DatabaseField
from ...model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class Querier:
    """
    Abstraction of query_repository for query_panel
    """

    def __init__(self, plan_enum_str: str):
        self.plan_enum = LandUsePlanEnum[plan_enum_str]
        self.plan: Optional[LandUsePlan] = None
        self.qr: Optional[QueryRepository] = None
        self._fields: Dict[str, DatabaseField] = {}
        self._initialize()

    def _initialize(self):
        self.plan: LandUsePlan.__class__ = self.plan_enum.value
        conn_params = get_db_connection_params(self.plan_enum)
        self.qr = QueryRepository(conn_params, self.plan_enum)
        self._fields = self.plan.query_fields

    @property
    def fields(self) -> Dict[str, DatabaseField]:
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

    def fetch_choices(self, field: DatabaseField) -> Tuple[List, bool]:
        """
        Fetch choices for the field if any

        :param field: Database field
        :return: Choice list and whether choices are string or not
        """
        return self.qr.fetch_choices(field)

    def add_condition(self, field: DatabaseField, operation: Operation, value: str):
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
        :return:
        """
        rnd = lambda c: round(c, precision)
        self.qr.add_extent(
            rnd(extent.xMinimum()),
            rnd(extent.yMinimum()),
            rnd(extent.xMaximum()),
            rnd(extent.yMaximum())
        )