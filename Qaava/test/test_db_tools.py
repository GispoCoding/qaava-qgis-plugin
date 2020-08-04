import pytest

from .conftest import (remove_db_settings, CONN_NAME, QGIS_APP)
from ..core.db.db_utils import (get_existing_database_connections, set_qaava_connection,
                                get_db_connection_params)
from ..core.exceptions import QaavaDatabaseNotSetException
from ..model.land_use_plan import LandUsePlanEnum


# DB utils tests
def test_get_existing_database_connections_empty():
    remove_db_settings()
    connections = get_existing_database_connections()
    assert connections == set()


def test_get_existing_database_connections_1(initialize_db_settings):
    set_qaava_connection(LandUsePlanEnum.detailed, CONN_NAME)
    connections = get_existing_database_connections()
    assert connections == {CONN_NAME}


def test_qaava_connection_url_exception():
    with pytest.raises(QaavaDatabaseNotSetException):
        assert get_db_connection_params(LandUsePlanEnum.detailed, QGIS_APP)


def test_qaava_connection_params(initialize_db_settings, database_params):
    set_qaava_connection(LandUsePlanEnum.general, CONN_NAME)
    params = get_db_connection_params(LandUsePlanEnum.general, QGIS_APP)
    assert params == database_params


def test_qaava_connection_params_without_saving_username_and_pwd(initialize_db_settings2, database_params):
    set_qaava_connection(LandUsePlanEnum.detailed, CONN_NAME)
    params = get_db_connection_params(LandUsePlanEnum.detailed, QGIS_APP)
    expected_params = {**database_params, **{"user": None, "password": None}}
    assert params == expected_params


@pytest.mark.skip("Not implemented")
def test_qaava_connection_url_auth_cfg():
    """TODO: implement test"""
