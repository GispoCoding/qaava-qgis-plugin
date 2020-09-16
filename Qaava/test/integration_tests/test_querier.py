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

from qgis.core import QgsRectangle

from ...core.db.querier import Querier
from ...definitions.db import Operation
from ...model.land_use_plan import LandUsePlanEnum


def test_querier_fields(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    assert set(querier.fields.keys()) == {'gid', 'uuid', 'nimi', 'kaavatunnus', 'laatija',
                                          'viimeisin_muokkaaja', 'vahvistaja', 'luomispvm',
                                          'poistamispvm', 'voimaantulopvm', 'kumoamispvm',
                                          'Vaihetieto.nimi', 'Vaihetieto.kuvaus'}


def test_query_repository_initialization(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    query = querier.show_query()
    assert query == 'SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" '


def test_querier_extent(general_db):
    extent = QgsRectangle(23456138, 6695226, 23456935, 6695726)
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_extent(extent)
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" WHERE "geom" && '
                     'ST_MakeEnvelope(23456138.0, 6695226.0, 23456935.0, 6695726.0, 27310)')
    assert len(querier.run()) == 1


def test_fetch_land_use_with_status(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_condition(querier.fields['Vaihetieto.nimi'], Operation.EQ, 'aloitusvaihe')
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" LEFT JOIN '
                     '"koodistot"."vaihetieto" ON "gid_vaihetieto"="koodistot"."vaihetieto"."gid" '
                     'WHERE "koodistot"."vaihetieto"."nimi"=\'aloitusvaihe\'')
    assert len(querier.run()) == 4


def test_chained_query_1(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_condition(querier.fields['luomispvm'], Operation.LT, '2020-09-09 15:10:04')
    querier.add_condition(querier.fields['Vaihetieto.nimi'], Operation.LIKE, 'aloit%svaihe')
    querier.add_condition(querier.fields['nimi'], Operation.GTE, '')
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" LEFT JOIN '
                     '"koodistot"."vaihetieto" ON "gid_vaihetieto"="koodistot"."vaihetieto"."gid" '
                     'WHERE "luomispvm"<\'2020-09-09 15:10:04\' AND  '
                     '"koodistot"."vaihetieto"."nimi" LIKE \'aloit%svaihe\' AND  "nimi" IS NULL')
