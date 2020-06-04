import pytest

from ..database_tools.database import Database
from ..database_tools.db_initializer import DatabaseInitializer
from .conftest import set_settings, CONN_NAME, IFACE, QGIS_APP


def test_database_select(docker_database_params):
    db = Database(docker_database_params["db1"])
    rows = db.execute_select("SELECT * FROM test_table")
    assert rows == [(1,)]


def test_db_initializer_with_detailed_plan(new_project, docker_database_params, monkeypatch):
    set_settings(docker_database_params["db2"])
    db = Database(docker_database_params["db2"])

    def mock_db():
        return CONN_NAME

    def mock_plan():
        return "detailed"

    initializer = DatabaseInitializer(IFACE, QGIS_APP)

    monkeypatch.setattr(initializer.dlg, "get_db", mock_db)
    monkeypatch.setattr(initializer.dlg, "get_plan", mock_plan)

    initializer.initialize_database()

    rows = db.execute_select("SELECT nspname FROM pg_catalog.pg_namespace;")
    expected_schemas = {('asemakaavat',), ('koodistot',), ('kaavan_lisatiedot',)}

    assert set(rows).intersection(expected_schemas) == expected_schemas
