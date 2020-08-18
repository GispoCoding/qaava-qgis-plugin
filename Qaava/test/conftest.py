"""
This class contains fixtures and common helper function to keep the test files shorter
"""

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

import os
import time
import timeit

import psycopg2
import pytest
from PyQt5.QtCore import QSettings
from qgis.core import QgsProject

from ..definitions.constants import PG_CONNECTIONS
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.testing.utilities import get_qgis_app, is_running_inside_ci

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# noinspection PyArgumentList
QGIS_INSTANCE = QgsProject.instance()

CONN_NAME = "test_qaava_conn"


@pytest.fixture(scope='function')
def new_project() -> None:
    """Initializes new iface project"""
    yield IFACE.newProject()


@pytest.fixture(scope='function')
def initialize_db_settings(database_params) -> str:
    set_settings(database_params)
    yield CONN_NAME
    remove_db_settings()


@pytest.fixture(scope='function')
def initialize_db_settings2(database_params):
    set_settings(database_params, has_pwd=False)
    yield CONN_NAME
    remove_db_settings()


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:
    """ Points to test docker-compose file"""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.yml")


@pytest.fixture(scope="session")
def database_params() -> {str: str}:
    params = {"dbname": "qaavadb1", "user": "postgres", "host": "localhost", "password": "postgres", "port": "5439"}
    return params


if not is_running_inside_ci():
    @pytest.fixture(scope='session')
    def db(docker_ip, docker_services, database_params) -> {str: {str: str}}:
        """

        :param docker_ip: pytest-docker fixture
        :param docker_services:  pytest-docker fixture
        :param database_params: fixture
        :return: db params in a dict
        """
        port = docker_services.port_for("qaava-test-db", 5432)
        params = {**database_params, **{"port": port}}
        params_for_detailed = {**params, **{"dbname": "qaava-detailed"}}
        params_for_general = {**params, **{"dbname": "qaava-general"}}
        wait_until_responsive(
            timeout=10.0, pause=1, check=lambda: is_responsive(params)
        )
        return {
            "db1": params,
            "detailed": params_for_detailed,
            "general": params_for_general
        }
else:
    @pytest.fixture(scope='session')
    def db(database_params) -> {str: {str: str}}:
        """
        database paramse fixture using database running in CI environment
        :param database_params: fixture
        :return: db params in a dict
        """
        params = {**database_params}
        params_for_detailed = {**params, **{"dbname": "qaava-detailed"}}
        params_for_general = {**params, **{"dbname": "qaava-general"}}
        wait_until_responsive(
            timeout=10.0, pause=1, check=lambda: is_responsive(params)
        )

        return {
            "db1": params,
            "detailed": params_for_detailed,
            "general": params_for_general
        }


def wait_until_responsive(check, timeout, pause, clock=timeit.default_timer):
    """
    Wait until a service is responsive.
    Taken from docker_services.wait_until_responsive
    """

    ref = clock()
    now = ref
    while (now - ref) < timeout:
        if check():
            return
        time.sleep(pause)
        now = clock()

    raise Exception("Timeout reached while waiting on service!")


def is_responsive(params):
    succeeds = False
    try:
        with(psycopg2.connect(**params)) as conn:
            succeeds = True
    except psycopg2.OperationalError as e:
        pass
    return succeeds


def set_settings(prms, has_pwd=True):
    s = QSettings()
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/host", prms["host"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/port", prms["port"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/database", prms["dbname"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/username", prms["user"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/password", prms["password"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/savePassword", "true" if has_pwd else "false")
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/saveUsername", "true" if has_pwd else "false")
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/authcfg", "NULL")


def remove_db_settings():
    s = QSettings()
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/host")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/port")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/database")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/username")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/password")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/savePassword")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/saveUsername")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/authcfg")
    s.remove(LandUsePlanEnum.detailed.value.key)
    s.remove(LandUsePlanEnum.general.value.key)
