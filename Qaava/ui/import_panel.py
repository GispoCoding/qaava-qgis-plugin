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

from typing import List, Dict

from .base_panel import BasePanel
from ..definitions.qui import Panels
from ..qgis_plugin_tools.tools.exceptions import QgsPluginNotImplementedException

class ImportPanel(BasePanel):
    """ Panel for importing data into the database from a layer """

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Import

    def setup_panel(self):
        self._populate_layer_combobox()
        self._populate_table_combobox()
        self.dlg.layer_combo_box.layerChanged.connect(self.__layer_changed)
        self.dlg.q_combo_box_table.currentTextChanged.connect(self.__table_changed)
        self.dlg.q_push_button_import.clicked.connect(self.__run_import)

    def _populate_layer_combobox(self):
        """ Populates the layer combo box with map layers that are not inside groups """
        raise QgsPluginNotImplementedException

    def _populate_table_combobox(self):
        """ Populates the table combo box with database tables """
        tables = self.__get_database_tables()
        self.dlg.q_combo_box_table.addItems(tables)

    def __get_database_tables(self) -> List[str]:
        """ Gets database tables that are valid targets for insert.
        Code tables should not be returned. """
        raise QgsPluginNotImplementedException

    def __layer_changed(self):
        """ Triggered when user changes the layer to import from """
        # if no table selected: return
        # get active layer from self.dlg.layer_combo_box
        # read layer fields
        # for all form rows, set combo box available values to match layer fields
        raise QgsPluginNotImplementedException

    def __table_changed(self):
        """ Triggered when user changes the target table """
        # table_columns = self.__get_table_columns(self.dlg.q_combo_box_table.currentText)
        # set self.dlg.form_layout_column_mapping so nr. of rows matches nr. of columns in table
        # update label for each form layout row so all table columns have a corresponding label
        # update combo boxes for each form row, same as self.__layer_changed
        raise QgsPluginNotImplementedException

    def __get_table_columns(self, table_name: str) -> Dict:
        """ Gets columns from database for table """
        # should return a dict {"column_name": "column_type"}
        raise QgsPluginNotImplementedException

    def __run_import(self):
        """ Imports data to database after user clicks the import button """
        self._start_process()
        # try:
        # create a new empty vector layer
        # generate fields for new layer to match with db columns
        # read original layer field -> db column translation input from form UI
        # populate new layer with features from original layer using translation
        # append features from new layer to table using qgis processing algorithm
        # except: abort import, no data should be imported to db
        self._end_process()
        raise QgsPluginNotImplementedException
