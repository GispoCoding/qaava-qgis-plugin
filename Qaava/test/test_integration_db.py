import pytest

from .conftest import set_settings, CONN_NAME, IFACE, QGIS_APP
from ..core.db.database import Database
from ..core.db.db_initializer import DatabaseInitializer
from ..qgis_plugin_tools.testing.utilities import is_running_inside_ci


@pytest.mark.skipif(is_running_inside_ci(), reason="CI")
def test_database_select(docker_database_params):
    content_of_test_database_select(docker_database_params["db1"])


@pytest.mark.skipif(is_running_inside_ci(), reason="CI")
def test_db_initializer_with_detailed_plan(new_project, docker_database_params):
    content_of_test_db_initializer_with_detailed_plan(docker_database_params["db2"])


# CI tests
@pytest.mark.skipif(not is_running_inside_ci(), reason="Not in CI")
def test_database_select_ci(ci_database_params):
    content_of_test_database_select(ci_database_params["db1"])


@pytest.mark.skipif(not is_running_inside_ci(), reason="Not in CI")
def test_db_initializer_with_detailed_plan_ci(new_project, ci_database_params):
    content_of_test_db_initializer_with_detailed_plan(ci_database_params["db2"])


# noinspection SqlNoDataSourceInspection
def content_of_test_database_select(params):
    db = Database(params)
    rows = db.execute_select("SELECT * FROM test_table")
    assert rows == [(1,)]


# noinspection SqlNoDataSourceInspection
def content_of_test_db_initializer_with_detailed_plan(prms):
    set_settings(prms)
    db = Database(prms)

    initializer = DatabaseInitializer(IFACE, QGIS_APP)
    initializer.initialize_database(CONN_NAME, "detailed")
    rows = db.execute_select("SELECT nspname FROM pg_catalog.pg_namespace;")
    expected_schemas = {('asemakaavat',), ('koodistot',), ('kaavan_lisatiedot',)}
    assert set(rows).intersection(expected_schemas) == expected_schemas
