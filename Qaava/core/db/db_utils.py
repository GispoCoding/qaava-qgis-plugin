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

import logging

from PyQt5.QtCore import QSettings, QCoreApplication
from qgis.core import QgsAuthMethodConfig

from ...core.exceptions import QaavaDatabaseNotSetException, QaavaAuthConfigException
from ...definitions.constants import (PG_CONNECTIONS, QGS_SETTINGS_PSYCOPG2_PARAM_MAP)
from ...model.land_use_plan import LandUsePlanEnum
from ...qgis_plugin_tools.tools.resources import plugin_name
from ...qgis_plugin_tools.tools.settings import parse_value, set_setting, get_setting

LOGGER = logging.getLogger(plugin_name())


def get_existing_database_connections() -> {str}:
    """
    :return: set of connections names
    """
    s = QSettings()
    s.beginGroup(PG_CONNECTIONS)
    keys = s.allKeys()
    s.endGroup()
    connections = {key.split('/')[0] for key in keys if '/' in key}
    LOGGER.debug(f"Connections: {connections}")
    return connections


def set_qaava_connection(plan: LandUsePlanEnum, conn_name: str) -> None:
    """
    Set connection to be used as Qaava connection
    :param plan:
    :param conn_name:
    """
    set_setting(plan.value.key, conn_name, internal=False)


def get_qaava_connection_name(plan: LandUsePlanEnum) -> str:
    """
    :return: Name of the PostGIS connection that will be used by the plugin
    """
    value = get_setting(plan.value.key, "", str)
    if value == "":
        raise QaavaDatabaseNotSetException()
    return value


def get_db_connection_params(plan: LandUsePlanEnum, qgs_app: QCoreApplication) -> {str: str}:
    """
    :return: Psycopg2 connection params for Qaava database
    """

    s = QSettings()
    s.beginGroup(f"{PG_CONNECTIONS}/{get_qaava_connection_name(plan)}")
    auth_cfg_id = parse_value(s.value("authcfg"))
    username_saved = parse_value(s.value("saveUsername"))
    pwd_saved = parse_value(s.value("savePassword"))

    params = {}

    for qgs_key, psyc_key in QGS_SETTINGS_PSYCOPG2_PARAM_MAP.items():
        params[psyc_key] = parse_value(s.value(qgs_key))

    s.endGroup()
    # username or password might have to be asked separately
    if not username_saved:
        params["user"] = None

    if not pwd_saved:
        params["password"] = None

    if auth_cfg_id is not None and auth_cfg_id != "":
        LOGGER.info(f"Auth cfg: {auth_cfg_id}")
        # Auth config is being used to store the username and password
        auth_config = QgsAuthMethodConfig()
        qgs_app.authManager().loadAuthenticationConfig(auth_cfg_id, auth_config, True)

        if auth_config.isValid():
            params["user"] = auth_config.configMap().get("username")
            params["password"] = auth_config.configMap().get("password")
        else:
            raise QaavaAuthConfigException()

    LOGGER.info(f"PR{params} {username_saved} {pwd_saved}")

    return params
