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

from typing import Union, List, Optional, Dict

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import Composed


class Database:

    def __init__(self, conn_params: {str: str}):
        self.conn_params = conn_params

    def is_valid(self) -> bool:
        """
        Tests whether database connection is valid or not
        :return:
        """
        succeeds = False
        try:
            with(psycopg2.connect(**self.conn_params)) as conn:
                succeeds = True
        except psycopg2.OperationalError:
            pass
        return succeeds

    def execute_insert(self, query: str) -> None:
        """
        Execute insert, drop, delete or update queries
        :param query: query string
        :return:
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)

    def execute_select(self, query: Union[str, Composed], vars: Optional[Dict] = None,
                       ret_dict: object = False) -> List[object]:
        """
        Execute select query and return fetched results

        :param query: query string or psycopg2 Composed
        :param vars: query variables
        :param ret_dict: Whether to return list of dicts or
        :return: rows
        """

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor if ret_dict else None) as cur:
                cur.execute(query, vars=vars)
                return cur.fetchall()
