import logging

from PyQt5.QtWidgets import QDialog

from .about_panel import AboutPanel
from .db_panel import DbPanel
from .settings_panel import SettingsPanel
from ..definitions.qui import Panels
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name

FORM_CLASS = load_ui('main_dialog.ui')
LOGGER = logging.getLogger(plugin_name())


class Dialog(QDialog, FORM_CLASS):
    """
    The structure and idea of the UI is adapted from https://github.com/3liz/QuickOSM
    licenced under GPL version 2
    """

    def __init__(self, iface, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.iface = iface

        self.panels = {
            Panels.Database: DbPanel(self),
            Panels.Settings: SettingsPanel(self),
            Panels.About: AboutPanel(self)
        }

        self.responsive_elements = {
            Panels.Database: {self.dbComboBox, self.dmComboBox, self.refreshPushButton, self.agreedCheckBox,
                              self.btn_db_initialize},
            Panels.Settings: [],
            Panels.About: []
        }

        for i, panel in enumerate(self.panels):
            item = self.menu_widget.item(i)
            item.setIcon(panel.icon)

        # Change panel as menu item is changed
        self.menu_widget.currentRowChanged['int'].connect(
            self.stacked_widget.setCurrentIndex)

        try:
            for panel in self.panels.values():
                panel.setup_panel()
        except Exception as e:
            LOGGER.exception(tr(u"Unhandled exception occurred during UI initialization."), bar_msg(e))

        self.menu_widget.setCurrentRow(0)
