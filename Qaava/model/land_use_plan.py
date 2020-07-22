import enum
from typing import Union

from ..definitions.constants import DETAILED_PLAN_DATA_MODEL_URL, QAAVA_DB_NAME
from ..qgis_plugin_tools.tools.exceptions import QgsPluginNotImplementedException
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
    schema_url = None  # TODO: fill schema url when in use

    def fetch_schema(self) -> str:
        raise QgsPluginNotImplementedException()


class LandUsePlanEnum(enum.Enum):
    detailed = DetailedLandUsePlan
    general = GeneralLandUsePlan
