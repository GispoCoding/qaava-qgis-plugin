from PyQt5.QtCore import QSettings
from ...utils.constants import (PG_CONNECTIONS, QAAVA_DB_NAME, QGS_SETTINGS_PSYCOPG2_PARAM_MAP)
from ...utils import logger
from ...utils.exceptions import QaavaDatabaseNotSet


def get_existing_database_connections() -> {str}:
    """
    :return: set of connections names
    """
    s = QSettings()
    s.beginGroup(PG_CONNECTIONS)
    keys = s.allKeys()
    s.endGroup()
    connections = {key.split('/')[0] for key in keys if '/' in key}
    logger.debug(str(connections))
    return connections


def set_qaava_connection(conn_name: str) -> None:
    """
    Set connection to be used as Qaava connection
    :param conn_name:
    """
    QSettings().setValue(QAAVA_DB_NAME, conn_name)


def get_qaava_connection_name() -> str:
    """
    :return: Name of the PostGIS connection that will be used by the plugin
    """
    value = QSettings().value(QAAVA_DB_NAME, "", str)
    if value == "":
        raise QaavaDatabaseNotSet()
    return value


def get_db_connection_url() -> str:
    """
    :return: Psycopg2 connection url for Qaava database
    """
    s = QSettings()
    s.beginGroup(f"{PG_CONNECTIONS}/{get_qaava_connection_name()}")
    url = "dbname={dbname} user={user} host={host} password={password} port={port}"
    params = {}
    for qgs_key, psyc_key in QGS_SETTINGS_PSYCOPG2_PARAM_MAP.items():
        params[psyc_key] = s.value(qgs_key)
    s.endGroup()
    return url.format(**params)
