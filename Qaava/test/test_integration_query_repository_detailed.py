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
from ..core.db.querier import Querier
from ..core.db.query_repository import QueryRepository
from ..definitions.db import Operation
from ..model.common import ProcessInfo
from ..model.land_use_plan import LandUsePlanEnum


# noinspection SqlResolve
def test_query_repository_initialization(detailed_db):
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    query = repository.show_query()
    assert query == 'SELECT pl."gid" FROM "asemakaavat"."asemakaava" pl '


def test_querier_fields(detailed_connection_set):
    querier = Querier(LandUsePlanEnum.detailed.name)
    assert querier.fields == {'vaihetieto.nimi': ProcessInfo.name}


# noinspection SqlResolve
def test_query_status_1(detailed_db):
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    repository.set_status(1, Operation.EQ)
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "asemakaavat"."asemakaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE p."gid"=1')


def test_fetch_available_status_codes(detailed_db):
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    codes = repository.fetch_available_status_codes()
    assert len(codes) == 8
    assert {'gid': 1, 'name': 'valmisteluvaihe'} in codes


def test_fetch_land_use_with_status(detailed_db):
    # TODO: add test data
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    repository.set_status(1, Operation.EQ)
    plans = repository.run_query()
    assert len(plans) == 0
