import logging

from .base_panel import BasePanel
from ..definitions.qui import Panels
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..qgis_plugin_tools.tools.version import version

LOGGER = logging.getLogger(plugin_name())


class AboutPanel(BasePanel):

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.About

    def setup_panel(self):
        v = version()
        LOGGER.info(tr(u"Plugin version is " + v))
        self.dlg.label_version.setText(v)
