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

from .base_panel import BasePanel, process
from .db_panel import DbPanel
from ..core.db.db_utils import get_qaava_connection_name
from ..definitions.qui import Panels
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class QaavaPanel(BasePanel):

    def __init__(self, dialog, db_panel: DbPanel):
        super().__init__(dialog)
        self.db_panel = db_panel
        self.panel = Panels.Qaava
        self.plan_enum: LandUsePlanEnum = LandUsePlanEnum.general

    def setup_panel(self):
        self.dlg.btn_qaava_general.clicked.connect(lambda: self._start_qaava_session(LandUsePlanEnum.general))
        self.dlg.btn_qaava_detailed.clicked.connect(lambda: self._start_qaava_session(LandUsePlanEnum.detailed))

    @process
    def _start_qaava_session(self, plan_enum: LandUsePlanEnum):
        LOGGER.debug(f'Initializing session with {plan_enum.name} plan')
        self.plan_enum = plan_enum

        # set values
        self.dlg.dbComboBox.setCurrentText(get_qaava_connection_name(plan_enum))
        self.dlg.dmComboBox.setCurrentText(plan_enum.name)

        # Register and open project
        self.db_panel.register()
        self.db_panel.open_project()

        LOGGER.info(tr('Qaava session initialized'),
                    extra=bar_msg(tr('Qaava initialized successfully with plan {}', plan_enum.name),
                                  success=True))
