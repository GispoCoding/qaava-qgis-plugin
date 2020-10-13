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
from typing import List, Optional

from qgis.core import QgsApplication

from .base_panel import BasePanel, process
from ..core.db.db_initializer import DatabaseInitializer
from ..core.db.db_utils import get_existing_database_connections
from ..core.db.qgis_project_utils import load_project
from ..definitions.qui import Panels
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.decorations import log_if_fails
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class DbPanel(BasePanel):

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Database
        self.initializer: Optional[DatabaseInitializer] = None

    def setup_panel(self):
        self.populate_dbComboBox()
        self.populate_dmComboBox()

        self.dlg.refreshPushButton.clicked.connect(self.on_refreshPushButton_clicked)
        self.dlg.agreedCheckBox.clicked.connect(self.on_agreedCheckBox_stateChanged)
        self.dlg.dbComboBox.currentTextChanged.connect(lambda _: self._reset_gui())
        self.dlg.dmComboBox.currentTextChanged.connect(lambda _: self._reset_gui())
        self.dlg.cb_projects.currentTextChanged.connect(
            lambda _: self.dlg.btn_db_open_project.setEnabled(len(self.dlg.cb_projects.currentText()) > 0))

        # Run connections
        self.dlg.btn_db_initialize.clicked.connect(self.run)
        self.dlg.btn_db_open_project.clicked.connect(self.open_project)
        self.dlg.btn_db_register.clicked.connect(self.register)
        self.dlg.db_btn_promote.clicked.connect(self.promote)

        self._reset_gui()

    def _reset_gui(self):
        self.set_available_projects([])
        self.dlg.agreedCheckBox.setChecked(False)
        self.on_agreedCheckBox_stateChanged()
        self.set_versions()

    def teardown_panel(self):
        super().teardown_panel()
        self.initializer = None

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

    def set_available_projects(self, projects: List[str]):
        self.dlg.cb_projects.clear()
        self.dlg.cb_projects.addItems(projects)

    def set_versions(self, curr_version: str = '', newest_version: str = ''):
        self.dlg.db_l_curr_version.setText(curr_version)
        self.dlg.db_l_new_version.setText(newest_version)
        self.dlg.db_btn_promote.setEnabled(curr_version != newest_version)

    def get_db(self) -> str:
        return self.dlg.dbComboBox.currentText()

    def get_plan(self) -> str:
        return self.dlg.dmComboBox.currentText()

    def _run(self):
        # noinspection PyArgumentList
        self.initializer = DatabaseInitializer(self.dlg, QgsApplication.instance())
        self.initializer.initialize_database(self.get_db(), self.get_plan())
        LOGGER.info(tr('Database Initialized'),
                    extra=bar_msg(
                        tr('Database {} initialized succesfully with plan {}', self.get_db(), self.get_plan()),
                        success=True))
        projects = self.initializer.get_available_projects()
        self.set_available_projects(projects)
        self.set_versions(*self.initializer.get_versions())

    @process
    def open_project(self):
        project_name = self.dlg.cb_projects.currentText()
        if len(project_name):
            plan_enum = LandUsePlanEnum[self.get_plan()]
            load_project(project_name, plan_enum)
            self.dlg.on_update_map_layers()

    @process
    def register(self):
        # noinspection PyArgumentList
        self.initializer = DatabaseInitializer(self.dlg, QgsApplication.instance())
        self.initializer.register_database(self.get_db(), self.get_plan())
        LOGGER.info(tr(f'Database registered'), extra=bar_msg(self.get_db(), success=True))
        projects = self.initializer.get_available_projects()
        self.set_available_projects(projects)
        self.set_versions(*self.initializer.get_versions())

    @log_if_fails
    def promote(self):
        should_continue = self.dlg.ask_confirmation(tr('This action might result to QGIS project loss'),
                                                    tr('This action will delete all QGIS projects saved in the '
                                                       'database. If you want to save your current project, please '
                                                       'press "Cancel" and save the project to disk '
                                                       'before continuing.'))
        if should_continue:
            self.initializer.promote_database()
            LOGGER.info(tr(f'Database promoted', ),
                        extra=bar_msg(tr('Promoted from version {} to version {}', self.dlg.db_l_curr_version.text(),
                                         self.dlg.db_l_new_version.text()), success=True))
            self.set_versions(*self.initializer.get_versions())
        else:
            LOGGER.debug('Cancelled promotion')
