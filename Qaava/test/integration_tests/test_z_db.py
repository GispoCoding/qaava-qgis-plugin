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
from ..conftest import set_settings, IFACE, QGIS_APP, CONN_NAME, remove_db_settings
from ...core.db.database import Database
from ...core.db.db_initializer import DatabaseInitializer
from ...qgis_plugin_tools.tools.version import version_from_string

'''
Add here integration tests that should be run last
'''


def test_migrations_for_detailed(new_project, detailed_db_old):
    prms = detailed_db_old
    set_settings(prms)
    try:
        db = Database(prms)
        rows = db.execute_select('SELECT versio FROM koodistot.tietomalli_metatiedot')
        assert rows == [('0.1.0',)]
        initializer = DatabaseInitializer(IFACE, QGIS_APP)
        initializer.register_database(CONN_NAME, "detailed")
        current_version, is_outdated = initializer.is_schema_outdated()
        assert current_version == (0, 1, 0)
        assert is_outdated
        initializer.promote_database()
        rows = db.execute_select('SELECT versio FROM koodistot.tietomalli_metatiedot')
        assert version_from_string(rows[0][0]) >= (0, 2, 0)
    finally:
        remove_db_settings()
