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

import enum
from typing import Union, Dict

from ..core.db.qgis_project_utils import fix_data_sources_from_binary_projects
from ..definitions.constants import (DETAILED_PLAN_DATA_MODEL_URL, QAAVA_DB_NAME, GENERAL_PLAN_DATA_MODEL_URL)
from ..qgis_plugin_tools.tools.network import fetch
from ..qgis_plugin_tools.tools.resources import resources_path


class LandUsePlan:
    key = ""
    auth_cfg_id = ""
    schema_url = ""
    newest_version = None
    enum = None

    def __init__(self):
        self.raw_schema: Union[str, None] = None
        self.schema: Union[str, None] = None

    def fetch_schema(self) -> str:
        """
        Fetch schema from the schema_url
        :return: schema sql
        """
        self.raw_schema = fetch(self.schema_url)
        self._alter_schema()  # TODO: This is just temporary solution, remove when this is not needed anymore
        return self.schema

    def fetch_project(self, conn_params: Dict[str, str], auth_cfg_id: str) -> str:
        """
        :return: project sql
        """
        # TODO: fetch from github

        with open(resources_path('qgis_projects.sql')) as f:
            content = f.read()
        content = self.fix_project(auth_cfg_id, conn_params, content)

        return content

    def fix_project(self, auth_cfg_id, conn_params, content):
        proj_bytes = [line.split(',')[5][4:-3] for line in content.split('\n') if
                      line.startswith('INSERT INTO public.qgis_projects')]
        byts = [bytes.fromhex(b) for b in proj_bytes]
        ret_vals = fix_data_sources_from_binary_projects(conn_params, auth_cfg_id=auth_cfg_id, contents=byts)
        for i in range(len(proj_bytes)):
            content = content.replace(proj_bytes[i], ret_vals[i].decode('utf-8'))
        return content

    def _alter_schema(self):
        """
        Alters raw schemas so that it will work even in populated databases and with any owner
        :return:
        """
        schema_lines = []
        for line in self.raw_schema.split("\n"):
            if (line.startswith("-- DROP ") or line.startswith("-- ALTER")) and "EXTENSION" not in line:
                line = line.replace("-- ", "")
            if "OWNER TO postgres" in line:
                line = "-- " + line
            if line.startswith("CREATE EXTENSION"):
                line = line.replace("CREATE EXTENSION", "CREATE EXTENSION IF NOT EXISTS")

            schema_lines.append(line)
        self.schema = "\n".join(schema_lines)


class DetailedLandUsePlan(LandUsePlan):
    key = f"{QAAVA_DB_NAME}/detailed"
    auth_cfg_key = f"{key}/auth_cfg"
    schema_url = DETAILED_PLAN_DATA_MODEL_URL


class GeneralLandUsePlan(LandUsePlan):
    key = f"{QAAVA_DB_NAME}/general"
    auth_cfg_key = f"{key}/auth_cfg"
    schema_url = GENERAL_PLAN_DATA_MODEL_URL


class LandUsePlanEnum(enum.Enum):
    detailed = DetailedLandUsePlan
    general = GeneralLandUsePlan
