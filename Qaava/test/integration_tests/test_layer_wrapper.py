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

from ...core.wrappers.layer_wrapper import LayerWrapper


def test_simple_wrapper(general_db):
    lw = LayerWrapper("Yleiskaava", "gid")
    assert lw.get_layer().isValid()


def test_get_fields(general_db):
    lw = LayerWrapper("Yleiskaava", "uuid")
    fields = lw.get_fields(3, False)
    fields = {f.alias: f for f in fields}
    assert list(fields.keys()) == [
        "nimi",
        "kaavatunnus",
        "laatija",
        "viimeisin_muokkaaja",
        "vahvistaja",
        "luomispvm",
        "poistamispvm",
        "voimaantulopvm",
        "kumoamispvm",
    ]

    assert "sanna_gispo" in fields["viimeisin_muokkaaja"].unique_values


def test_get_child_fields(general_db):
    lw = LayerWrapper("Yleiskaava", "uuid")
    fields = lw.get_fields(10, True)
    fields = {f.alias: f for f in fields}
    assert list(fields.keys()) == [
        "nimi",
        "kaavatunnus",
        "laatija",
        "viimeisin_muokkaaja",
        "vahvistaja",
        "luomispvm",
        "poistamispvm",
        "voimaantulopvm",
        "kumoamispvm",
        "Has Vaihetieto",
        "Vaihetieto.nimi",
        "Vaihetieto.kuvaus",
        "Dokumentti.otsikko",
        "Dokumentti.uri",
        "Has Dokumentti",
        "Kaavamääräys.luontipvm",
        "Kaavamääräys.otsikko",
        "Kaavamääräys.maaraysteksti",
        "Has Kaavamääräys",
    ]
    assert fields["Vaihetieto.nimi"].unique_values == {
        "hyväksytty",
        "valmisteluvaihe",
        "lainvoimainen",
        "keskeytetty",
        "aloitusvaihe",
        "hyväksymisvaihe",
        "kumottu",
        "luonnosvaihe",
        "ehdotusvaihe",
    }
    assert fields["Kaavamääräys.otsikko"].unique_values == {
        "yleismääräys1",
        "Testausmääräys",
        "Toimiihan tämä",
    }
