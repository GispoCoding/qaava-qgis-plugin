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

import os
import time
import timeit

import psycopg2
import pytest
from PyQt5.QtCore import QSettings
from qgis.core import (QgsProject, QgsApplication, QgsVectorLayer, QgsDataSourceUri, QgsRelation, QgsRelationManager)

from ..core.db.database import Database
from ..core.db.db_utils import set_qaava_connection, set_auth_cfg
from ..definitions.constants import PG_CONNECTIONS
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.testing.utilities import get_qgis_app, is_running_inside_ci
from ..qgis_plugin_tools.tools.resources import plugin_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# noinspection PyArgumentList
QGIS_INSTANCE = QgsProject.instance()

CONN_NAME = "test_qaava_conn"


@pytest.fixture(scope='function')
def new_project() -> None:
    """Initializes new iface project"""
    remove_db_settings()
    yield IFACE.newProject()


@pytest.fixture(scope='function')
def initialize_db_settings(database_params) -> str:
    set_settings(database_params)
    yield CONN_NAME
    remove_db_settings()


@pytest.fixture(scope='function')
def general_connection_set(initialize_db_settings):
    set_qaava_connection(LandUsePlanEnum.general, CONN_NAME)


@pytest.fixture(scope='function')
def initialize_db_settings2(database_params):
    set_settings(database_params, has_pwd=False)
    yield CONN_NAME
    remove_db_settings()


'''
For integration tests

Database remains the same during tests, use db fixture in tests that run before general_db.

TEST FILE NAMING IS IMPORTANT! Tests are run in alphabetical order!

For example:
# Good
test_a.py
    def test_1(db):
        ...
test_b.py
    def test_1(general_db):
        ...

# Bad
test_a.py
    def test_1(general_db):
        ...
test_b.py
    def test_1(db):
        ...
'''


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
        params_for_general_old = {**params, **{"dbname": "qaava-general-old"}}
        params_for_detailed_old = {**params, **{"dbname": "qaava-detailed-old"}}
        wait_until_responsive(
            timeout=20.0, pause=1, check=lambda: is_responsive(params)
        )
        return {
            "db1": params,
            "detailed": params_for_detailed,
            "general": params_for_general,
            "general_old": params_for_general_old,
            "detailed_old": params_for_detailed_old
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
        params_for_general_old = {**params, **{"dbname": "qaava-general-old"}}
        params_for_detailed_old = {**params, **{"dbname": "qaava-detailed -old"}}
        wait_until_responsive(
            timeout=20.0, pause=1, check=lambda: is_responsive(params)
        )
        return {
            "db1": params,
            "detailed": params_for_detailed,
            "general": params_for_general,
            "general_old": params_for_general_old,
            "detailed_old": params_for_detailed_old
        }


@pytest.fixture(scope='session')
def general_db(db):
    params = db['general']
    insert_sql(params, 'general_plan_0.2.0.sql')
    insert_sql(params, 'general_data_0.2.0.sql')

    # Set settings and auth config
    set_settings(params, has_pwd=False, auth_cfg=CONN_NAME)
    set_qaava_connection(LandUsePlanEnum.general, CONN_NAME)

    initialize_auth_manager()
    set_auth_cfg(LandUsePlanEnum.general, CONN_NAME, params['user'], params['password'])

    # Add project to db
    # # Commented out because tests can not use it at the moment
    # with open(get_test_resource('db_fixtures', 'general_plan_project_0.2.0.sql')) as f:
    #     content = fix_project(auth_cfg_id=CONN_NAME, conn_params=params, content=f.read())
    # insert_sql(params, sql_content=content)

    # Add layers and relations
    common_uri = f'dbname=\'{params["dbname"]}\' host={params["host"]} port={params["port"]} sslmode=disable authcfg={CONN_NAME}'

    # Feel free to add more layers and relations. Easiest way to get the source string is QgsVectorLayer.source()
    layers = {
        # geometry layers
        'Yleiskaava': f'{common_uri} key=\'uuid\' srid=3877 type=MultiPolygonZ checkPrimaryKeyUnicity=\'1\' table="yleiskaava"."yleiskaava" (geom)',
        'Maankäyttöalue': f'{common_uri} key=\'uuid\' srid=3877 type=MultiPolygonZ checkPrimaryKeyUnicity=\'1\' table="yleiskaava"."maankayttoalue" (geom)',

        # table layers
        'Vaihetieto': f'{common_uri} key=\'gid\' checkPrimaryKeyUnicity=\'1\' table="koodistot"."vaihetieto"',
        'Dokumentti': f'{common_uri} key=\'gid\' checkPrimaryKeyUnicity=\'1\' table="kaavan_lisatiedot"."dokumentti"',
        'Kaavamääräys': f'{common_uri} key=\'uuid\' checkPrimaryKeyUnicity=\'1\' table="koodistot"."kaavamaarays"',

        # relation layers
        'many_dokumentti_has_many_yleiskaava': f'{common_uri} key=\'gid_dokumentti,uuid_yleiskaava\' checkPrimaryKeyUnicity=\'1\' table="kaavan_lisatiedot"."many_dokumentti_has_many_yleiskaava"',
        'many_yleiskaava_has_many_kaavamaarays': f'{common_uri} key=\'uuid_yleiskaava,uuid_kaavamaarays\' checkPrimaryKeyUnicity=\'1\' table="yleiskaava"."many_yleiskaava_has_many_kaavamaarays"',
    }

    relations = {
        'vaihetieto_fk': ('Vaihetieto', 'gid', 'Yleiskaava', 'gid_vaihetieto'),
        'Yleiskaavan maankäyttöalueet': ('Yleiskaava', 'uuid', 'Maankäyttöalue', 'uuid_yleiskaava'),
        'Yleiskaavan dokumentit': ('Yleiskaava', 'uuid', 'many_dokumentti_has_many_yleiskaava', 'uuid_yleiskaava'),
        'Dokumentin kaavat': ('Dokumentti', 'gid', 'many_dokumentti_has_many_yleiskaava', 'gid_dokumentti'),
        'Yleiskaavan kaavamääräykset': (
            'Yleiskaava', 'uuid', 'many_yleiskaava_has_many_kaavamaarays', 'uuid_yleiskaava'),
        'kaavamaarays_yleis': ('Kaavamääräys', 'uuid', 'many_yleiskaava_has_many_kaavamaarays', 'uuid_kaavamaarays'),
    }

    inserted_ids = {}

    for name, uri in layers.items():
        layer = QgsVectorLayer(QgsDataSourceUri(uri).uri(False), name, 'postgres')
        assert layer.isValid()
        inserted_ids[name] = layer.id()
        QGIS_INSTANCE.addMapLayer(layer)

    # noinspection PyArgumentList
    relation_manager: QgsRelationManager = QgsProject.instance().relationManager()
    for name, rel_params in relations.items():
        rel = QgsRelation()
        rel.setId(name)
        rel.setName(name)
        rel.setReferencedLayer(inserted_ids[rel_params[0]])
        rel.setReferencingLayer(inserted_ids[rel_params[2]])
        rel.addFieldPair(rel_params[3], rel_params[1])
        relation_manager.addRelation(rel)

    yield params
    remove_db_settings()


@pytest.fixture(scope='session')
def detailed_db(db):
    params = db['detailed']
    insert_sql(params, 'detailed_plan_0.2.0.sql')
    return params


@pytest.fixture(scope='session')
def detailed_db_old(db):
    params = db['detailed_old']
    insert_sql(params, 'detailed_plan_0.1.0.sql')
    return params


'''
####################
Helper functions
###################
'''


def clean_schema(raw_schema: str) -> str:
    schema_lines = []
    for line in raw_schema.split("\n"):
        if (line.startswith("-- DROP ") or line.startswith("-- ALTER")) and "EXTENSION" not in line:
            line = line.replace("-- ", "")
        if "OWNER TO postgres" in line:
            line = "-- " + line
        if line.startswith("CREATE EXTENSION"):
            line = line.replace("CREATE EXTENSION", "CREATE EXTENSION IF NOT EXISTS")

        schema_lines.append(line)
    return "\n".join(schema_lines)


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


def set_settings(prms, has_pwd=True, auth_cfg="NULL"):
    s = QSettings()
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/host", prms["host"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/port", prms["port"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/database", prms["dbname"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/username", prms["user"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/password", prms["password"])
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/savePassword", "true" if has_pwd else "false")
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/saveUsername", "true" if has_pwd else "false")
    s.setValue(f"{PG_CONNECTIONS}/{CONN_NAME}/authcfg", auth_cfg)


def initialize_auth_manager():
    """
    From https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/authentication.html#init-the-manager-and-set-the-master-password
    """
    # check if QgsAuthManager has already been initialized... a side effect
    # of the QgsAuthManager.init() is that AuthDbPath is set.
    # QgsAuthManager.init() is executed during QGIS application init and hence
    # you do not normally need to call it directly.

    # noinspection PyArgumentList
    authMgr = QgsApplication.authManager()

    if authMgr.authenticationDatabasePath():
        # already initilised => we are inside a QGIS app.
        if authMgr.masterPasswordIsSet():
            msg = 'Authentication master password not recognized'
            assert authMgr.masterPasswordSame("salasana"), msg
        else:
            msg = 'Master password could not be set'
            # The verify parameter check if the hash of the password was
            # already saved in the authentication db
            assert authMgr.setMasterPassword("salasana", verify=True), msg
    else:
        # outside qgis, e.g. in a testing environment => setup env var before
        # db init
        os.environ['QGIS_AUTH_DB_DIR_PATH'] = get_test_resource('test_data', 'qgis-auth.db')
        if not authMgr.masterPasswordIsSet():
            msg = 'Master password could not be set'
            assert authMgr.setMasterPassword("salasana", True), msg
        else:
            msg = 'Authentication master password not recognized'
            assert authMgr.masterPasswordSame("salasana"), msg
        authMgr.init(get_test_resource('test_data', 'qgis-auth.db'))


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
    s.remove(LandUsePlanEnum.detailed.value.auth_cfg_key)
    s.remove(LandUsePlanEnum.general.value.auth_cfg_key)
    # noinspection PyArgumentList
    QgsApplication.authManager().removeAuthSetting(CONN_NAME)


def get_test_resource(*args: str) -> str:
    return plugin_path('test', *args)


def insert_sql(params, sql_file=None, sql_content=None):
    db = Database(params)
    if sql_file is not None:
        with open(get_test_resource('db_fixtures', sql_file)) as f:
            sql = f.read()
            db.execute_insert(clean_schema(sql))
    if sql_content is not None:
        db.execute_insert(clean_schema(sql_content))
