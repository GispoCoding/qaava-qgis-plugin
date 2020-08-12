from typing import List, Optional, Dict

from psycopg2.sql import Composed, SQL

from .database import Database
from ...model.common import ProcessInfo
from ...model.general_plan import ZoningPlan


# noinspection PyUnresolvedReferences
class QueryRepository(Database):
    def fetch_available_status_codes(self, additional_sql: Composed = SQL(''),
                                     vars: Optional[Dict] = None) -> List[ProcessInfo.Type]:
        query = (SQL('SELECT {gid}, {name} as name FROM {processInfo}')
                 .format(processInfo=ProcessInfo.table(), gid=ProcessInfo.gid,
                         name=ProcessInfo.name)) + additional_sql

        return self.execute_select(query, vars, ret_dict=True)

    def fetch_zoning_plans_with_status(self, status_gid: int, additional_sql: Composed = SQL(''),
                                       vars: Optional[Dict] = None) -> List[int]:
        query = (SQL('SELECT z.{z_gid} '
                     'FROM {zoningPlan} z LEFT JOIN {processInfo} p ON {rel}=p.{p_gid}'
                     'WHERE p.{p_gid} = %(status)s')
                 .format(zoningPlan=ZoningPlan.table(), processInfo=ProcessInfo.table(), rel=ZoningPlan.process_info.id,
                         z_gid=ZoningPlan.gid, p_gid=ProcessInfo.gid)) + additional_sql

        vars = dict(**vars, **{'status': status_gid}) if vars else {'status': status_gid}
        return [row[0] for row in self.execute_select(query, vars)]
