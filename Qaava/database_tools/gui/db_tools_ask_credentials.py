# -*- coding: utf-8 -*-
import os

from qgis.PyQt import QtWidgets
from qgis.PyQt import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'db_tools_ask_credentials_dialog.ui'))


class DbAskCredentialsDialog(QtWidgets.QDialog, FORM_CLASS):
    onCloseHandler = None

    def __init__(self, username: str, pwd: str, parent=None):
        """Constructor."""

        super(DbAskCredentialsDialog, self).__init__(parent)
        self.setupUi(self)

        if username is not None:
            self.userLineEdit.setText(username)

        if pwd is not None:
            self.pwdLineEdit.setText(pwd)
