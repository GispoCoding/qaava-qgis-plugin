from .conftest import set_settings, CONN_NAME, IFACE, QGIS_APP
from ..core.db.database import Database
from ..core.db.db_initializer import DatabaseInitializer


# noinspection SqlNoDataSourceInspection
def test_database_select(db):
    params = db["db1"]
    db1 = Database(params)
    rows = db1.execute_select("SELECT * FROM test_table")
    assert rows == [(1,)]


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
