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
from Qaava.core.wrappers.layer_wrapper import LayerWrapper


def test_simple_wrapper(general_db_with_data_and_layers):
    lw = LayerWrapper('Yleiskaava', 'gid')
    assert lw.get_layer().isValid()


def test_get_fields(general_db_with_data_and_layers):
    lw = LayerWrapper('Yleiskaava', 'gid')
    fields = lw.get_fields(3, False)
    field_names = [f.name for f in fields]
    assert field_names == ['gid', 'uuid', 'nimi', 'kaavatunnus', 'laatija',
                           'viimeisin_muokkaaja', 'vahvistaja', 'luomispvm',
                           'poistamispvm', 'voimaantulopvm', 'kumoamispvm']

    assert 'sanna_gispo' in fields[5].unique_values


def test_get_child_fields(general_db_with_data_and_layers):
    lw = LayerWrapper('Yleiskaava', 'gid')
    fields = lw.get_fields(10, True)
    field_names = [f.alias for f in fields]
    assert field_names == ['gid', 'uuid', 'nimi', 'kaavatunnus', 'laatija',
                           'viimeisin_muokkaaja', 'vahvistaja', 'luomispvm',
                           'poistamispvm', 'voimaantulopvm', 'kumoamispvm',
                           'Vaihetieto.nimi', 'Vaihetieto.kuvaus']
    assert fields[11].unique_values == {'hyväksytty', 'valmisteluvaihe', 'lainvoimainen', 'keskeytetty', 'aloitusvaihe',
                                        'hyväksymisvaihe', 'kumottu', 'luonnosvaihe', 'ehdotusvaihe'}
