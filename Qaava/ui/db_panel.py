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

import logging

from qgis.core import QgsApplication

from .base_panel import BasePanel
from ..core.db.db_initializer import DatabaseInitializer
from ..core.db.db_utils import get_existing_database_connections
from ..definitions.qui import Panels
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class DbPanel(BasePanel):

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Database

    def setup_panel(self):
        self.populate_dbComboBox()
        self.populate_dmComboBox()

        self.dlg.refreshPushButton.clicked.connect(self.on_refreshPushButton_clicked)
        self.dlg.agreedCheckBox.clicked.connect(self.on_agreedCheckBox_stateChanged)
        self.dlg.btn_db_initialize.clicked.connect(self.run)

        self.dlg.agreedCheckBox.setChecked(False)
        self.on_agreedCheckBox_stateChanged()

    def populate_dbComboBox(self):
        self.dlg.dbComboBox.clear()
        connections = get_existing_database_connections()
        for conn in connections:
            self.dlg.dbComboBox.addItem(conn)

    def populate_dmComboBox(self):
        self.dlg.dmComboBox.clear()
        for plan in [pl.name for pl in LandUsePlanEnum]:
            self.dlg.dmComboBox.addItem(plan)

    def on_refreshPushButton_clicked(self):
        self.populate_dbComboBox()

    def on_agreedCheckBox_stateChanged(self):
        self.dlg.btn_db_initialize.setEnabled(self.dlg.agreedCheckBox.isChecked())

    def get_db(self):
        return self.dlg.dbComboBox.currentText()

    def get_plan(self):
        return self.dlg.dmComboBox.currentText()

    def _run(self):
        # noinspection PyArgumentList
        initializer = DatabaseInitializer(self.dlg, QgsApplication.instance())
        initializer.initialize_database(self.get_db(), self.get_plan())
