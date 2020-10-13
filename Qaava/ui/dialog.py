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

from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog, QMessageBox

from .about_panel import AboutPanel
from .db_panel import DbPanel
from .qaava_panel import QaavaPanel
from .query_panel import QueryPanel
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
        self.is_running = False

        db_panel = DbPanel(self)
        self.panels = {
            Panels.Qaava: QaavaPanel(self, db_panel),
            Panels.Query: QueryPanel(self),
            Panels.Database: db_panel,
            Panels.Settings: SettingsPanel(self),
            Panels.About: AboutPanel(self)
        }

        self.responsive_elements = {
            Panels.Qaava: [self.btn_qaava_general, self.btn_qaava_detailed],
            Panels.Query: [self.q_push_button_reset, self.q_push_button_refresh, self.query_grid,
                           self.q_push_button_add_row, self.q_push_button_show_query,
                           self.q_push_button_run_query, self.q_push_button_clear_filter, self.q_combo_box_layer],
            Panels.Database: [self.dbComboBox, self.dmComboBox, self.refreshPushButton, self.agreedCheckBox,
                              self.btn_db_initialize, self.btn_db_register, self.btn_db_open_project, self.cb_projects,
                              self.db_btn_promote],
            Panels.Settings: [],
            Panels.About: []
        }

        for i, panel in enumerate(self.panels):
            item = self.menu_widget.item(i)
            item.setIcon(panel.icon)
            self.panels[panel].panel = panel

        # Change panel as menu item is changed
        self.menu_widget.currentRowChanged['int'].connect(
            self.stacked_widget.setCurrentIndex)

        try:
            for panel in self.panels.values():
                panel.setup_panel()
        except Exception as e:
            LOGGER.exception(tr(u'Unhandled exception occurred during UI initialization.'), bar_msg(e))

        # The first panel is shown initially
        self.menu_widget.setCurrentRow(0)

    def ask_confirmation(self, title: str, msg: str) -> bool:
        """
        Ask confirmation via QMessageBox question
        :param title: title of the window
        :param msg: message of the window
        :return: Whether user wants to continue
        """
        res = QMessageBox.information(self, title, msg, QMessageBox.Ok, QMessageBox.Cancel)
        return res == QMessageBox.Ok

    def closeEvent(self, evt: QtGui.QCloseEvent) -> None:
        LOGGER.debug('Closing dialog')
        try:
            for panel in self.panels.values():
                panel.teardown_panel()
        except Exception as e:
            LOGGER.exception(tr(u'Unhandled exception occurred during UI closing.'), bar_msg(e))

    def on_update_map_layers(self):
        LOGGER.debug('Updating map layers')
        try:
            for panel in self.panels.values():
                panel.on_update_map_layers()
        except Exception as e:
            LOGGER.exception(tr(u'Unhandled exception occurred while updating map layers.'), bar_msg(e))
