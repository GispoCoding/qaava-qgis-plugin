"""Panel core base class."""
import logging

from PyQt5.QtWidgets import QDialog

from ..definitions.qui import Panels
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.exceptions import QgsPluginException, QgsPluginNotImplementedException
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class BasePanel:
    """
    Base panel for dialog. Adapted from https://github.com/3liz/QuickOSM
    licenced under GPL version 2
    """

    def __init__(self, dialog: QDialog):
        self._panel = None
        self._dialog = dialog

    @property
    def panel(self) -> Panels:
        if self._panel:
            return self._panel
        else:
            raise NotImplemented

    @panel.setter
    def panel(self, panel: Panels):
        self._panel = panel

    @property
    def dlg(self) -> QDialog:
        """Return the dialog.
        """
        return self._dialog

    def setup_panel(self):
        """Setup the UI for the panel."""
        raise QgsPluginNotImplementedException

    def run(self):
        self._start_process()
        try:
            self._run()
        except QgsPluginException as e:
            LOGGER.exception(tr(u"Unhandled plugin exception occurred. Details: "), bar_msg(e))
        except Exception as e:
            LOGGER.exception(tr(u"Unhandled exception occurred. Details: "), bar_msg(e))
        finally:
            self._end_process()

    def _run(self):
        raise QgsPluginNotImplementedException

    def _start_process(self):
        """Make some stuff before launching the process."""
        for elem in self.dlg.responsive_elements[self.panel]:
            elem.setEnabled(False)

    def _end_process(self):
        """Make some stuff after the process."""
        for elem in self.dlg.responsive_elements[self.panel]:
            elem.setEnabled(True)
