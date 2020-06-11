import pytest

from .conftest import set_settings, CONN_NAME, IFACE, QGIS_APP
from .utilities import is_running_inside_CI
from ..database_tools.database import Database
from ..database_tools.db_initializer import DatabaseInitializer


@pytest.mark.skipif(is_running_inside_CI(), reason="CI")
def test_database_select(docker_database_params):
    content_of_test_database_select(docker_database_params["db1"])


@pytest.mark.skipif(is_running_inside_CI(), reason="CI")
def test_db_initializer_with_detailed_plan(new_project, docker_database_params, monkeypatch):
    content_of_test_db_initializer_with_detailed_plan(docker_database_params["db2"], monkeypatch)


# CI tests
@pytest.mark.skipif(not is_running_inside_CI(), reason="Not in CI")
def test_database_select_ci(ci_database_params):
    content_of_test_database_select(ci_database_params["db1"])


@pytest.mark.skipif(not is_running_inside_CI(), reason="Not in CI")
def test_db_initializer_with_detailed_plan_ci(new_project, ci_database_params, monkeypatch):
    content_of_test_db_initializer_with_detailed_plan(ci_database_params["db2"], monkeypatch)


def content_of_test_database_select(params):
    db = Database(params)
    rows = db.execute_select("SELECT * FROM test_table")
    assert rows == [(1,)]


def content_of_test_db_initializer_with_detailed_plan(prms, monkeypatch):
    set_settings(prms)
    db = Database(prms)

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
