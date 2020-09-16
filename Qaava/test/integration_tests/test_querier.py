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
    assert set(querier.fields.keys()) == {'Dokumentti.gid', 'Dokumentti.otsikko', 'Dokumentti.uri',
                                          'Kaavamääräys.luontipvm', 'Kaavamääräys.maaraysteksti',
                                          'Kaavamääräys.otsikko', 'Kaavamääräys.uuid', 'Vaihetieto.gid',
                                          'Vaihetieto.kuvaus', 'Vaihetieto.nimi', 'gid', 'kaavatunnus', 'kumoamispvm',
                                          'laatija', 'luomispvm', 'nimi', 'poistamispvm', 'uuid', 'vahvistaja',
                                          'viimeisin_muokkaaja', 'voimaantulopvm'}


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


def test_querier_land_use_with_status(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_condition(querier.fields['Vaihetieto.nimi'], Operation.EQ, 'aloitusvaihe')
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" LEFT JOIN '
                     '"koodistot"."vaihetieto" ON '
                     '"yleiskaava"."gid_vaihetieto"="koodistot"."vaihetieto"."gid" WHERE '
                     '"vaihetieto"."nimi"=\'aloitusvaihe\'')
    assert len(querier.run()) == 4


def test_querier_document_with_title(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_condition(querier.fields['Dokumentti.otsikko'], Operation.EQ, 'Kukkakauppias')
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" LEFT JOIN '
                     '"kaavan_lisatiedot"."many_dokumentti_has_many_yleiskaava" ON '
                     '"many_dokumentti_has_many_yleiskaava"."uuid_yleiskaava"="yleiskaava"."uuid" '
                     'LEFT JOIN "kaavan_lisatiedot"."dokumentti" ON '
                     '"many_dokumentti_has_many_yleiskaava"."gid_dokumentti"="dokumentti"."gid" '
                     'WHERE "dokumentti"."otsikko"=\'Kukkakauppias\'')
    assert len(querier.run()) == 0


def test_querier_order(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_condition(querier.fields['Kaavamääräys.otsikko'], Operation.EQ, 'Testausmääräys')
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" LEFT JOIN '
                     '"yleiskaava"."many_yleiskaava_has_many_kaavamaarays" ON '
                     '"many_yleiskaava_has_many_kaavamaarays"."uuid_yleiskaava"="yleiskaava"."uuid" '
                     'LEFT JOIN "koodistot"."kaavamaarays" ON '
                     '"many_yleiskaava_has_many_kaavamaarays"."uuid_kaavamaarays"="kaavamaarays"."uuid" '
                     'WHERE "kaavamaarays"."otsikko"=\'Testausmääräys\'')
    assert len(querier.run()) == 3


def test_chained_query_1(general_db):
    querier = Querier(LandUsePlanEnum.general.name)
    querier.add_condition(querier.fields['luomispvm'], Operation.LT, '2020-09-09 15:10:04')
    querier.add_condition(querier.fields['Vaihetieto.nimi'], Operation.LIKE, 'aloit%svaihe')
    querier.add_condition(querier.fields['nimi'], Operation.GTE, '')
    query = querier.show_query()
    assert query == ('SELECT "yleiskaava"."uuid" FROM "yleiskaava"."yleiskaava" LEFT JOIN '
                     '"koodistot"."vaihetieto" ON '
                     '"yleiskaava"."gid_vaihetieto"="koodistot"."vaihetieto"."gid" WHERE '
                     '"yleiskaava"."luomispvm"<\'2020-09-09 15:10:04\' AND  "vaihetieto"."nimi" '
                     'LIKE \'aloit%svaihe\' AND  "yleiskaava"."nimi" IS NULL')
