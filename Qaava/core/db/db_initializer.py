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

import psycopg2
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog

from .database import Database
from .db_utils import (set_qaava_connection, get_db_connection_params, set_auth_cfg)
from ...core.exceptions import QaavaAuthConfigException
from ...model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginNetworkException, QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.resources import plugin_name
from ...ui.db_tools_ask_credentials import DbAskCredentialsDialog

LOGGER = logging.getLogger(plugin_name())


class DatabaseInitializer:

    def __init__(self, dialog: QDialog, qgs_app: QCoreApplication) -> None:
        self.dlg = dialog
        self.qgs_app = qgs_app

    def initialize_database(self, db_conn_name: str, plan_sting: str) -> None:
        """
        Initialize database for the land use planning
        :return:
        """
        plan_enum = LandUsePlanEnum[plan_sting]
        plan: LandUsePlan = plan_enum.value()  # intance of plan class because of ()

        try:
            set_qaava_connection(plan_enum, db_conn_name)
            conn_params = get_db_connection_params(plan_enum)
        except QaavaAuthConfigException as e:
            LOGGER.error(tr(u"Auth config error occurred while fetching database connection parameters:"),
                         extra=bar_msg(e))
            return
        except Exception as e:
            LOGGER.error(tr(u"Error occurred while fetching database connection parameters:"), extra=bar_msg(e))
            return

        # Ask username and password if needed
        if conn_params["user"] is None or conn_params["password"] is None:
            ask_credentials_dlg = DbAskCredentialsDialog(conn_params["user"], conn_params["password"])
            result = ask_credentials_dlg.exec_()
            if result:
                conn_params["user"] = ask_credentials_dlg.userLineEdit.text()
                conn_params["password"] = ask_credentials_dlg.pwdLineEdit.text()
            else:
                LOGGER.warning(tr(u"Canceling"),
                               extra=bar_msg(tr(u"Could not continue initializing without username and password")))
                return

        # Save credentials to auth config
        set_auth_cfg(plan_enum, db_conn_name, conn_params["user"], conn_params["password"])
        database = Database(conn_params)

        if not database.is_valid():
            LOGGER.warning(tr(u"Database connection error"),
                           extra=bar_msg(tr(u"Could not access the database.")))
            return

        try:
            schema_query = plan.fetch_schema()
            project_query = plan.fetch_project(conn_params, db_conn_name)
        except QgsPluginNetworkException as e:
            LOGGER.error(tr(u"Network error:"),
                         extra=bar_msg(
                             tr(u"Could not load schema for the plan. Check your internet connection. Details: ") + str(
                                 e)))
            return
        except QgsPluginNotImplementedException:
            LOGGER.warning(tr(u"Not implemented:"),
                           extra=bar_msg(tr(u"Schema for the selected plan is not implemented yet")))
            return

        try:
            # Actual insertion of the schema and project
            database.execute_insert(schema_query)
            database.execute_insert(project_query)
        except psycopg2.OperationalError:
            LOGGER.error(tr(u"Connection error:"),
                         extra=bar_msg(tr(u"Could not connect to the database: ") + db_conn_name))
            return
        except (Exception, psycopg2.DatabaseError) as e:
            LOGGER.error(tr(u"Error occurred while injecting schema:"),
                         extra=bar_msg(e))
            return

        LOGGER.info(tr(u"Success"),
                    extra=bar_msg(tr(u"Database initialized succesfully with land use plan ") + plan_enum.name,
                                  success=True))
