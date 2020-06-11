"""
This class contains fixtures and common helper function to keep the test files shorter
"""

import os
import timeit
import time

import pytest

import psycopg2
from PyQt5.QtCore import QSettings
from qgis.core import QgsProject

from .utilities import get_qgis_app
from ..model.land_use_plan import LandUsePlanEnum
from ..utils.constants import PG_CONNECTIONS

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
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


@pytest.fixture(scope='session')
def docker_database_params(docker_ip, docker_services, database_params) -> {str: {str: str}}:
    """

    :param docker_ip: pytest-docker fixture
    :param docker_services:  pytest-docker fixture
    :param database_params: fixture
    :return: db params in a dict
    """
    port = docker_services.port_for("qaava-test-db", 5432)
    params = {**database_params, **{"port": port}}
    params2 = {**params, **{"dbname": "qaavadb2"}}
    wait_until_responsive(
        timeout=10.0, pause=1, check=lambda: is_responsive(params)
    )
    return {
        "db1": params,
        "db2": params2
    }


@pytest.fixture(scope='session')
def ci_database_params(database_params) -> {str: {str: str}}:
    """
    database paramse fixture using database running in CI environment
    :param database_params: fixture
    :return: db params in a dict
    """
    params = {**database_params}
    params2 = {**params, **{"dbname": "qaavadb2"}}
    wait_until_responsive(
        timeout=10.0, pause=1, check=lambda: is_responsive(params)
    )

    return {
        "db1": params,
        "db2": params2
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
