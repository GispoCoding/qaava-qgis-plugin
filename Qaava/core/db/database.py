from typing import Tuple

import psycopg2


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

    def execute_select(self, query: str) -> [Tuple]:
        """
        Execute select query and return fetched results
        :param query: query string
        :return: rows
        """

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
