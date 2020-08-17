import logging
from typing import List, Dict, Tuple

from psycopg2.sql import SQL, Composable

from .database import Database
from ...definitions.db import Operation
from ...model.common import ProcessInfo, DatabaseField
from ...model.detailed_plan import DetailedPlan
from ...model.general_plan import ZoningPlan
from ...model.land_use_plan import LandUsePlanEnum
from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


# noinspection PyUnresolvedReferences
class QueryRepository(Database):

    def __init__(self, conn_params: Dict[str, str], plan_enum: LandUsePlanEnum):
        super().__init__(conn_params)
        self.plan_enum = plan_enum
        self.select_parts: List[Composable] = []
        self.from_parts: List[Composable] = []
        self.where_parts: List[Composable] = []
        self.vars: Dict[str, any] = {}
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

    def fetch_choices(self, field: DatabaseField) -> Tuple[List[str], bool]:
        """

        :return: Choice list and whether choices are string or not
        """
        if field == ProcessInfo.name:
            codes = self.fetch_available_status_codes()
            return [f"{code['gid']}: {code['name']}" for code in codes], False
        else:
            return [], True

    def fetch_available_status_codes(self) -> List[ProcessInfo.Type]:
        query = (SQL('SELECT {gid}, {name} as name FROM {processInfo}')
                 .format(processInfo=ProcessInfo.table(), gid=ProcessInfo.gid,
                         name=ProcessInfo.name.field))

        return self.execute_select(query, ret_dict=True)

    def set_status(self, status_gid: int, operation: Operation):
        self.from_parts.append(
            SQL('LEFT JOIN {processInfo} p ON {rel}=p.{p_gid}')
                .format(processInfo=ProcessInfo.table(), rel=ZoningPlan.process_info.field, p_gid=ProcessInfo.gid)
        )
        self.where_parts.append(
            SQL('p.{p_gid}' + operation.value + '%(status)s').format(p_gid=ProcessInfo.gid)
        )
        self.vars['status'] = status_gid

    def add_and_condition(self, field: DatabaseField, operation: Operation, value: any):
        if field == ProcessInfo.name:
            self.set_status(int(value.split(":")[0]), operation)
        else:
            self.where_parts.append(
                SQL('pl.{fld}' + operation.value + '%(' + str(field) + ')s').format(fld=field.field)
            )

            self.vars[str(field)] = value

    def run_query(self) -> List[int]:
        return [row[0] for row in self.execute_select(self.query, self.vars)]

    def show_query(self) -> str:
        return self.mogrify_query(self.query, self.vars)

    def _set_initial_parts(self):
        table = ZoningPlan if self.plan_enum == LandUsePlanEnum.general else DetailedPlan
        self.select_parts.append(SQL('SELECT pl.{gid}').format(gid=table.gid))
        self.from_parts.append(SQL('FROM {plan} pl').format(plan=table.table()))
