from PyQt5.QtCore import QSettings
from qgis.core import QgsAuthMethodConfig, QgsApplication

from ..model.land_use_plan import LandUsePlanEnum
from ..utils import logger
from ..utils.constants import (PG_CONNECTIONS, QGS_SETTINGS_PSYCOPG2_PARAM_MAP)
from ..utils.exceptions import QaavaDatabaseNotSetException, QaavaAuthConfigException
from ..utils.utils import parse_value


def get_existing_database_connections() -> {str}:
    """
    :return: set of connections names
    """
    s = QSettings()
    s.beginGroup(PG_CONNECTIONS)
    keys = s.allKeys()
    s.endGroup()
    connections = {key.split('/')[0] for key in keys if '/' in key}
    logger.debug(f"Connections: {connections}")
    return connections


def set_qaava_connection(plan: LandUsePlanEnum, conn_name: str) -> None:
    """
    Set connection to be used as Qaava connection
    :param plan:
    :param conn_name:
    """
    QSettings().setValue(plan.value.key, conn_name)


def get_qaava_connection_name(plan: LandUsePlanEnum) -> str:
    """
    :return: Name of the PostGIS connection that will be used by the plugin
    """
    value = QSettings().value(plan.value.key, "", str)
    if value == "":
        raise QaavaDatabaseNotSetException()
    return value


def get_db_connection_params(plan: LandUsePlanEnum, qgs_app: QgsApplication) -> {str: str}:
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
        logger.info(f"Auth cfg: {auth_cfg_id}")
        # Auth config is being used to store the username and password
        auth_config = QgsAuthMethodConfig()
        qgs_app.authManager().loadAuthenticationConfig(auth_cfg_id, auth_config, True)

        if auth_config.isValid():
            params["user"] = auth_config.configMap().get("username")
            params["password"] = auth_config.configMap().get("password")
        else:
            raise QaavaAuthConfigException()

    logger.info(f"PR{params} {username_saved} {pwd_saved}")

    return params
