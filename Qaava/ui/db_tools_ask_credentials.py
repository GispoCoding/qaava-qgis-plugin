# -*- coding: utf-8 -*-

from qgis.PyQt import QtWidgets

from ..qgis_plugin_tools.tools.resources import load_ui

FORM_CLASS = load_ui('db_tools_ask_credentials_dialog.ui')


class DbAskCredentialsDialog(QtWidgets.QDialog, FORM_CLASS):
    onCloseHandler = None

    def __init__(self, username: str, pwd: str, parent=None):
        """Constructor."""

        # noinspection PyArgumentList
        super(DbAskCredentialsDialog, self).__init__(parent)
        self.setupUi(self)

        if username is not None:
            self.userLineEdit.setText(username)

        if pwd is not None:
            self.pwdLineEdit.setText(pwd)
