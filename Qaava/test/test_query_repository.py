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

from qgis._core import QgsRectangle

from .conftest import CONN_NAME
from ..core.db.db_utils import set_qaava_connection
from ..core.db.querier import Querier
from ..core.db.query_repository import QueryRepository
from ..definitions.db import Operation
from ..model.land_use_plan import LandUsePlanEnum


def test_fetch_available_status_codes(general_db_schema_and_codes):
    repository = QueryRepository(general_db_schema_and_codes, LandUsePlanEnum.general)
    codes = repository.fetch_available_status_codes()
    assert len(codes) == 9
    assert {'gid': 1, 'name': 'aloitusvaihe'} in codes


def test_querier_fields(general_db_with_data_and_layers):
    # TODO: fix
    querier = Querier(LandUsePlanEnum.general.name)
    assert querier.fields == {}


def test_querier_extent(general_db_with_data_and_layers):
    set_qaava_connection(LandUsePlanEnum.general, CONN_NAME)
    extent = QgsRectangle().fromWkt(
        'POLYGON((23840873.5152964 6952581.91716873,23840873.5152964 6981622.5665375,23875214.1013225 6981622.5665375,23875214.1013225 6952581.91716873,23840873.5152964 6952581.91716873))')
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_extent(extent)
    query = querier.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl WHERE pl."geom" && '
                     'ST_MakeEnvelope(23840873.5153, 6952581.9172, 23875214.1013, 6981622.5665, '
                     '3877)')


def test_fetch_land_use_with_status(general_db_with_data):
    # TODO: add test data
    repository = QueryRepository(general_db_with_data, LandUsePlanEnum.general)
    repository.set_status(1, Operation.EQ)
    plans = repository.run_query()
    assert len(plans) == 0


def test_query_repository_initialization(general_db_schema_and_codes):
    repository = QueryRepository(general_db_schema_and_codes, LandUsePlanEnum.general)
    query = repository.show_query()
    assert query == 'SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl '


def test_query_repository_initialization_detailed(general_db_schema_and_codes):
    repository = QueryRepository(general_db_schema_and_codes, LandUsePlanEnum.detailed)
    query = repository.show_query()
    assert query == 'SELECT pl."gid" FROM "asemakaavat"."asemakaava" pl '


def test_query_status_1(general_db_schema_and_codes):
    repository = QueryRepository(general_db_schema_and_codes, LandUsePlanEnum.general)
    repository.set_status(1, Operation.EQ)
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE p."gid"=1')


def test_query_status_2(general_db_schema_and_codes):
    repository = QueryRepository(general_db_schema_and_codes, LandUsePlanEnum.general)
    repository.add_and_condition(ProcessInfo.name, Operation.GT, "1: aloitusvaihe")
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE p."gid">1')


def test_query_chained_1(general_db_schema_and_codes):
    # TODO: fix
    repository = QueryRepository(general_db_schema_and_codes, LandUsePlanEnum.general)
    repository.add_and_condition(ZoningPlan.name, Operation.EQ, "testplan")
    repository.add_and_condition(ZoningPlan.editor, Operation.LIKE, "ed%or")
    repository.add_and_condition(ProcessInfo.name, Operation.EQ, "1: aloitusvaihe")
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE '
                     'pl."nimi"=\'testplan\' AND  pl."laatija" LIKE \'ed%or\' AND  p."gid"=1')
