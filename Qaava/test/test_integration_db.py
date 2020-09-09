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

from .conftest import set_settings, CONN_NAME, IFACE, QGIS_APP
from ..core.db.database import Database
from ..core.db.db_initializer import DatabaseInitializer


# noinspection SqlNoDataSourceInspection
def test_database_select(db):
    params = db["db1"]
    db1 = Database(params)
    rows = db1.execute_select("SELECT * FROM test_table")
    assert rows == [(1,)]
    rows = db1.execute_select("SELECT * FROM test_table", ret_dict=True)
    assert rows[0] == {'?column?': 1}


# noinspection SqlNoDataSourceInspection
def test_db_initializer_with_detailed_plan(new_project, db):
    prms = db["detailed"]
    set_settings(prms)
    db1 = Database(prms)
    initializer = DatabaseInitializer(IFACE, QGIS_APP)
    initializer.initialize_database(CONN_NAME, "detailed")
    rows = db1.execute_select("SELECT nspname FROM pg_catalog.pg_namespace;")
    expected_schemas = {('asemakaavat',), ('koodistot',), ('kaavan_lisatiedot',)}
    assert set(rows).intersection(expected_schemas) == expected_schemas


# noinspection SqlNoDataSourceInspection
def test_db_initializer_with_general_plan(new_project, db):
    prms = db["general"]
    set_settings(prms)
    db1 = Database(prms)
    initializer = DatabaseInitializer(IFACE, QGIS_APP)
    initializer.initialize_database(CONN_NAME, "general")
    rows = db1.execute_select("SELECT nspname FROM pg_catalog.pg_namespace;")
    expected_schemas = {('yleiskaava',), ('koodistot',), ('kaavan_lisatiedot',)}
    assert set(rows).intersection(expected_schemas) == expected_schemas
    available_projects = initializer.get_available_projects()
    assert available_projects == ['qaava-yleiskaava']


def test_fixture_order_1(general_db_schema_and_codes):
    db1 = Database(general_db_schema_and_codes)
    rows = db1.execute_select("SELECT count(*) FROM yleiskaava.yleiskaava")
    assert rows == [(0,)]


def test_fixture_order_2(general_db_with_data):
    db1 = Database(general_db_with_data)
    rows = db1.execute_select("SELECT count(*) FROM yleiskaava.yleiskaava")
    assert rows == [(4,)]
