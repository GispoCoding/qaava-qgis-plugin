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

import pytest
from qgis.core import QgsProject

from ..conftest import get_test_resource, IFACE
from ...core.db.qgis_project_utils import (fix_project, load_project, fix_data_sources_from_binary_projects)
from ...model.land_use_plan import LandUsePlanEnum


def test_fix_project(database_params):
    with open(get_test_resource('db_fixtures', 'general_plan_project_0.2.0.sql')) as f:
        orig = f.read()
        fixed = fix_project('test_auth_cfg', database_params, orig)
        assert fixed != orig


def test_fix_project_with(database_params):
    conn_string = "dbname='qaavadb1' host=localhost port=5439 sslmode=disable authcfg=test_auth_cfg"
    with open(get_test_resource('test_data', 'general_project.qgz'), 'rb') as f:
        content = f.read()
    fixed = fix_data_sources_from_binary_projects(database_params, 'test_auth_cfg', [content], _test=True)[0]
    assert fixed.count(conn_string) == 241


@pytest.mark.skip('opening any project fails in test environment... Is there a solution for this?')
def test_loading_project(general_db):
    IFACE.newProject()
    load_project('qaava-yleiskaava', LandUsePlanEnum.general)
    # noinspection PyArgumentList
    layers = QgsProject.instance().mapLayers()
    assert len(layers) > 3
