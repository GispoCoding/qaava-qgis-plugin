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

import pytest

from .conftest import (remove_db_settings, CONN_NAME)
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
        assert get_db_connection_params(LandUsePlanEnum.detailed)


def test_qaava_connection_params(initialize_db_settings, database_params):
    set_qaava_connection(LandUsePlanEnum.general, CONN_NAME)
    params = get_db_connection_params(LandUsePlanEnum.general)
    assert params == database_params


def test_qaava_connection_params_without_saving_username_and_pwd(initialize_db_settings2, database_params):
    set_qaava_connection(LandUsePlanEnum.detailed, CONN_NAME)
    params = get_db_connection_params(LandUsePlanEnum.detailed)
    expected_params = {**database_params, **{"user": None, "password": None}}
    assert params == expected_params


@pytest.mark.skip("Not implemented")
def test_qaava_connection_url_auth_cfg():
    """TODO: implement test"""
