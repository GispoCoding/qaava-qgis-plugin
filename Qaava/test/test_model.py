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

from ..definitions.constants import DETAILED_PLAN_DATA_MODEL_URL
from ..model.land_use_plan import DetailedLandUsePlan, GeneralLandUsePlan
from ..qgis_plugin_tools.tools.exceptions import QgsPluginNetworkException
from ..qgis_plugin_tools.tools.network import fetch


def test_fetch(new_project):
    data_model = fetch(DETAILED_PLAN_DATA_MODEL_URL)
    assert len(data_model) > 10000


def test_fetch_invalid_url(new_project):
    with pytest.raises(QgsPluginNetworkException):
        fetch("invalidurl")


def test_detailed_plan_schema_fetch(new_project):
    plan = DetailedLandUsePlan()
    schema = plan.fetch_schema()
    assert len(schema) > 1000


def test_general_plan_schema_fetch(new_project):
    plan = GeneralLandUsePlan()
    schema = plan.fetch_schema()
    assert len(schema) > 1000


def test_general_plan_fetch_versions(new_project):
    plan = GeneralLandUsePlan()
    assert plan.newest_version >= (0, 0, 0)
    assert (0, 1, 0) in plan.available_versions


def test_project_fetch(new_project, database_params):
    plan = GeneralLandUsePlan()
    project_sql = plan.fetch_project(conn_params=database_params, auth_cfg_id='test-auth-cfg')
    assert len(project_sql) > 1000
