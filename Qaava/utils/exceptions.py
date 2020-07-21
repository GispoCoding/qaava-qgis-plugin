# Add application specific exception classes here
from ..qgis_plugin_tools.tools.exceptions import QgsPluginException


class QaavaDatabaseNotSetException(QgsPluginException):
    pass


class QaavaAuthConfigException(QgsPluginException):
    pass
