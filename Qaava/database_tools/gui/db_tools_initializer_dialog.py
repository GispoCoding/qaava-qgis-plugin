# -*- coding: utf-8 -*-
import os

from PyQt5.QtWidgets import QDialogButtonBox
from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis.gui import QgisInterface

from ..db_utils import get_existing_database_connections
from ...model.land_use_plan import LandUsePlanEnum
from ...utils.utils import tr

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'db_tools_initializer_dialog.ui'))


class DbInitializerDialog(QtWidgets.QDialog, FORM_CLASS):
    onCloseHandler = None

    def __init__(self, iface: QgisInterface, parent=None):
        """Constructor."""

        super(DbInitializerDialog, self).__init__(parent)
        self.setupUi(self)

        self.iface = iface

        self.populate_dbComboBox()
        self.populate_dmComboBox()

        self.buttonBox.button(QDialogButtonBox.Ok).setText(tr(u"Run"))

        self.agreedCheckBox.setChecked(False)
        self.on_agreedCheckBox_stateChanged()

    def populate_dbComboBox(self):
        self.dbComboBox.clear()
        connections = get_existing_database_connections()
        for conn in connections:
            self.dbComboBox.addItem(conn)

    def populate_dmComboBox(self):
        self.dmComboBox.clear()
        for plan in [pl.name for pl in LandUsePlanEnum]:
            self.dmComboBox.addItem(plan)

    def on_agreedCheckBox_stateChanged(self):
        self.buttonBox.setEnabled(self.agreedCheckBox.isChecked())

    def get_db(self):
        return self.dbComboBox.currentText()

    def get_plan(self):
        return self.dmComboBox.currentText()
