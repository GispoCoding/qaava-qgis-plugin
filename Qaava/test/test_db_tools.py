import pytest
from PyQt5.QtCore import QSettings
from qgis.gui import QgisInterface
from qgis.core import QgsProject
import psycopg2

from ..database_tools.src.db_utils import (get_existing_database_connections, set_qaava_connection,
                                           get_db_connection_url)
from .utilities import get_qgis_app
from ..utils.constants import (PG_CONNECTIONS, QAAVA_DB_NAME)
from ..utils.exceptions import QaavaDatabaseNotSet

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
QGIS_INSTANCE = QgsProject.instance()

CONN_NAME = "test_qaava_conn"


@pytest.fixture(scope='function')
def iface() -> QgisInterface:
    """Runs before every test. """
    yield IFACE.newProject()


@pytest.fixture(scope='function')
def initialize_db_settings(database_params):
    s = QSettings()
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/host", database_params["host"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/port", database_params["port"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/database", database_params["dbname"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/username", database_params["user"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/password", database_params["password"])
    yield CONN_NAME
    remove_db_settings()


def remove_db_settings():
    s = QSettings()
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/host")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/port")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/database")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/username")
    s.remove(f"{PG_CONNECTIONS}/{CONN_NAME}/password")
    s.remove(QAAVA_DB_NAME)


def test_get_existing_database_connections_empty() -> None:
    connections = get_existing_database_connections()
    assert connections == set()


def test_get_existing_database_connections_1(initialize_db_settings) -> None:
    set_qaava_connection(CONN_NAME)
    connections = get_existing_database_connections()
    assert connections == {CONN_NAME}


def test_qaava_connection_url_exception() -> None:
    with pytest.raises(QaavaDatabaseNotSet):
        assert get_db_connection_url()


def test_qaava_connection_url(initialize_db_settings, database_params) -> None:
    set_qaava_connection(CONN_NAME)
    url = get_db_connection_url()
    expected = "dbname={dbname} user={user} host={host} password={password} port={port}".format(**database_params)
    assert url == expected


@pytest.skip("This is just for testing the dockerized db, run if it is not working properly")
def test_docker_db(docker_database):
    with psycopg2.connect(docker_database["db1"]["url"]) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM test_table")
            res = [row[0] for row in curs][0]
            assert res == 1
