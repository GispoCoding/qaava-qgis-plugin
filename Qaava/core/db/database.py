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

import logging
from typing import Union, List, Optional, Dict

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Composable

from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class Database:
    sql_space = SQL(' ')
    sql_empty: Composable = SQL('')
    sql_and = SQL('AND ')
    sql_where = SQL('WHERE')

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

    def execute_insert(self, query: Union[str, Composable], vars: Optional[Dict] = None) -> None:
        """
        Execute insert, drop, delete or update queries
        :param query: query string or psycopg2 Composed
        :param vars: query variables
        :return:
        """

        LOGGER.debug(self.mogrify_query(query, vars))
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, vars=vars)

    def execute_select(self, query: Union[str, Composable], vars: Optional[Dict] = None,
                       ret_dict: object = False) -> List:
        """
        Execute select query and return fetched results

        :param query: query string or psycopg2 Composed
        :param vars: query variables
        :param ret_dict: Whether to return list of dicts or
        :return: rows
        """

        LOGGER.debug(self.mogrify_query(query, vars))
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor if ret_dict else None) as cur:
                cur.execute(query, vars=vars)
                return cur.fetchall()

    def mogrify_query(self, query: Union[str, Composable], vars: Optional[Dict] = None) -> str:
        """
        Returns query as string
        :param query:
        :param vars:
        :return:
        """

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                return cur.mogrify(query, vars=vars).decode("utf-8")

    def reduce_query(self, *query_parts: List[Composable]) -> Composable:
        """
        Reduce query to one Composable
        :param query_parts: list of Composable
        :return:
        """
        joined_parts = [self.sql_space.join(parts) for parts in query_parts]
        return self.sql_space.join(joined_parts)

    def reduce_where_parts(self, query_parts: List[Composable]) -> [Composable]:
        """
        Reduce where part of the query to one Composable
        :param query_parts: list of Composable
        :return:
        """
        return self.sql_where + self.sql_and.join(query_parts) if len(query_parts) else []
