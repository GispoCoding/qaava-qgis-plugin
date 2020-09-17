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

from ..qgis_plugin_tools.tools.settings import setting_key

# Urls
QAAVA_GITHUB_URL = "https://raw.githubusercontent.com/GispoCoding/qaava/master"

DETAILED_PLAN_DATA_MODEL_URL = f'{QAAVA_GITHUB_URL}/asemakaavan-tietomalli/tietomalli_luonnos.sql'
GENERAL_PLAN_URL = f'{QAAVA_GITHUB_URL}/yleiskaavan-tietomalli'
GENERAL_PLAN_MODEL_FILE_NAME = 'yleiskaavan-tietomalli.sql'
GENERAL_PLAN_PROJECT_FILE_NAME = 'yleiskaava-projekti.sql'

DETAILED_PLAN_URL = f'{QAAVA_GITHUB_URL}/asemakaavan-tietomalli'
DETAILED_PLAN_MODEL_FILE_NAME = 'asemakaavan-tietomalli.sql'
DETAILED_PLAN_PROJECT_FILE_NAME = 'asemakaava-projekti.sql'

VERSIONS_FILE_NAME = 'versions.txt'
MIGRATION_FILE_NAME = 'migraatio.sql'

# Database
PG_CONNECTIONS = "PostgreSQL/connections"
QAAVA_DB_NAME = setting_key("postgresqlConnectionName")

QGS_SETTINGS_PSYCOPG2_PARAM_MAP = {
    'database': 'dbname',
    'host': 'host',
    'password': 'password',
    'port': 'port',
    'username': 'user'
}

QGS_DEFAULT_DB_SETTINGS = {
    'allowGeometrylessTables': 'false',
    'authcfg': '',
    'dontResolveType': 'false',
    'estimatedMetadata': 'false',
    'geometryColumnsOnly': 'false',
    'projectsInDatabase': 'false',
    'publicOnly': 'false',
    'savePassword': 'true',
    'saveUsername': 'true',
    'service': '',
    'sslmode': 'SslDisable',
}

# Misc
