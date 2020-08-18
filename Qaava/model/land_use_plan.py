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

import enum
from typing import Union

from ..definitions.constants import (DETAILED_PLAN_DATA_MODEL_URL, QAAVA_DB_NAME, GENERAL_PLAN_DATA_MODEL_URL)
from ..qgis_plugin_tools.tools.network import fetch


class LandUsePlan:
    key = ""
    schema_url = ""
    available_versions = []
    newest_version = None

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
    schema_url = DETAILED_PLAN_DATA_MODEL_URL


class GeneralLandUsePlan(LandUsePlan):
    key = f"{QAAVA_DB_NAME}/general"
    schema_url = GENERAL_PLAN_DATA_MODEL_URL


class LandUsePlanEnum(enum.Enum):
    detailed = DetailedLandUsePlan
    general = GeneralLandUsePlan
