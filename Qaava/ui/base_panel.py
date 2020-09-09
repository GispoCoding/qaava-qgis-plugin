"""Panel core base class."""
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
        raise QgsPluginNotImplementedException()

    def teardown_panel(self):
        """Teardown for the panels"""

    def run(self, method='_run'):
        if not method:
            method = '_run'
        self._start_process()
        try:
            # use dispatch pattern to invoke method with same name
            if not hasattr(self, method):
                raise QgsPluginException(f'Class does not have a method {method}')
            getattr(self, method)()
        except QgsPluginException as e:
            LOGGER.exception(str(e), extra=e.bar_msg)
        except Exception as e:
            LOGGER.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))
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


def log_if_fails(fn):
    """
    Use this as a decorator with methods that might throw uncaught exceptions
    """
    from functools import wraps
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except QgsPluginException as e:
            LOGGER.exception(str(e), extra=e.bar_msg)
        except Exception as e:
            LOGGER.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))

    return wrapper
