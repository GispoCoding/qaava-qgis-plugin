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
import logging
from typing import Dict, List, Optional, Tuple, Union

from ..definitions.constants import (
    DETAILED_PLAN_MODEL_FILE_NAME,
    DETAILED_PLAN_PROJECT_FILE_NAME,
    DETAILED_PLAN_URL,
    GENERAL_PLAN_MODEL_FILE_NAME,
    GENERAL_PLAN_PROJECT_FILE_NAME,
    GENERAL_PLAN_URL,
    MIGRATION_FILE_NAME,
    QAAVA_DB_NAME,
    VERSIONS_FILE_NAME,
)
from ..qgis_plugin_tools.tools.network import fetch
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..qgis_plugin_tools.tools.version import string_from_version, version_from_string

LOGGER = logging.getLogger(plugin_name())


class LandUsePlan:
    key = ""
    auth_cfg_key = ""
    schema_url = ""
    versions_file = VERSIONS_FILE_NAME
    migration_file = MIGRATION_FILE_NAME
    url = ""
    file_name = ""
    project_file = ""

    def __init__(self):
        self.raw_schema: Optional[str] = None
        self.schema: Optional[str] = None
        self.raw_schema: Union[str, None] = None
        self.schema: Union[str, None] = None
        self.available_versions: Optional[List[Tuple[int, int, int]]] = None
        self.newest_version: Optional[Tuple[int, int, int]] = None
        self.fetch_versions()

    def fetch_versions(self):
        """
        Fetch version information of the model
        """
        self.available_versions = [
            version_from_string(v)
            for v in fetch(f"{self.url}/{self.versions_file}").strip().split("\n")
        ]
        self.newest_version = max(self.available_versions)
        LOGGER.debug(
            f"Newest version {self.newest_version}, available versions {self.available_versions}"
        )

    def create_migration_script(self, current_version: Tuple[int, int, int]):
        """
        Creates migration script
        :param current_version: current version of the schema
        :return: schema sql
        """
        migration_script = ""
        versions = [v for v in self.available_versions if v > current_version]
        for version in versions:
            migration_script += f"-- For version {string_from_version(version)}"
            migration_script += fetch(
                f"{self.url}/{string_from_version(version)}/{self.migration_file}"
            )
            migration_script += "\n\n"
        return migration_script

    def fetch_schema(self) -> str:
        """
        Fetch schema from the schema_url
        :return: schema sql
        """
        self.raw_schema = fetch(
            f"{self.url}/{string_from_version(self.newest_version)}/{self.file_name}"
        )
        self.schema = self.alter_schema(self.raw_schema)
        return self.schema

    def fetch_project(self, conn_params: Dict[str, str], auth_cfg_id: str) -> str:
        """
        Fetch QGIS project sql string. Might contain multiple projects
        :return: project sql string
        """
        # Import here in order to avoid circular import problem in tests
        from ..core.db.qgis_project_utils import fix_project

        content = fetch(
            f"{self.url}/{string_from_version(self.newest_version)}/{self.project_file}"
        )
        return fix_project(auth_cfg_id, conn_params, content)

    @staticmethod
    def alter_schema(script: str):
        """
        Alters raw schemas so that it will work even in populated databases and with any owner
        :return:
        """
        schema_lines = []
        for line in script.split("\n"):
            if (
                (line.startswith("-- DROP ") or line.startswith("-- ALTER"))
                and "EXTENSION" not in line
                and "DATABASE" not in line
            ):
                line = line.replace("-- ", "")
            if "OWNER TO postgres" in line:
                line = "-- " + line
            if line.startswith("CREATE EXTENSION"):
                line = line.replace(
                    "CREATE EXTENSION", "CREATE EXTENSION IF NOT EXISTS"
                )
            elif line.startswith("CREATE DATABASE"):
                line = line.replace("CREATE DATABASE", "-- CREATE DATABASE")

            schema_lines.append(line)
        return "\n".join(schema_lines)


class DetailedLandUsePlan(LandUsePlan):
    key = f"{QAAVA_DB_NAME}/detailed"
    auth_cfg_key = f"{key}/auth_cfg"
    url = DETAILED_PLAN_URL
    schema_url = DETAILED_PLAN_URL
    file_name = DETAILED_PLAN_MODEL_FILE_NAME
    project_file = DETAILED_PLAN_PROJECT_FILE_NAME


class GeneralLandUsePlan(LandUsePlan):
    key = f"{QAAVA_DB_NAME}/general"
    auth_cfg_key = f"{key}/auth_cfg"
    url = GENERAL_PLAN_URL
    schema_url = GENERAL_PLAN_URL
    file_name = GENERAL_PLAN_MODEL_FILE_NAME
    project_file = GENERAL_PLAN_PROJECT_FILE_NAME


class LandUsePlanEnum(enum.Enum):
    detailed = DetailedLandUsePlan
    general = GeneralLandUsePlan
