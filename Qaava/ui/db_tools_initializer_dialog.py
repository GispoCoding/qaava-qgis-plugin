# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialogButtonBox
from qgis.PyQt import QtWidgets

from ..core.db.db_utils import get_existing_database_connections
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import load_ui

FORM_CLASS = load_ui('db_tools_initializer_dialog.ui')


class DbInitializerDialog(QtWidgets.QDialog, FORM_CLASS):
    onCloseHandler = None

    def __init__(self, parent=None):
        """Constructor."""

        # noinspection PyArgumentList
        super(DbInitializerDialog, self).__init__(parent)
        self.setupUi(self)

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

    def on_refreshPushButton_clicked(self):
        self.populate_dbComboBox()

    def on_agreedCheckBox_stateChanged(self):
        self.buttonBox.setEnabled(self.agreedCheckBox.isChecked())

    def get_db(self):
        return self.dbComboBox.currentText()

    def get_plan(self):
        return self.dmComboBox.currentText()
