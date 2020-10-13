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
from typing import Optional, List, Dict, Tuple

import psycopg2
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog

from .database import Database
from .db_utils import (set_qaava_connection, get_db_connection_params, set_auth_cfg)
from ...core.exceptions import QaavaInitializationCancelled, QaavaDatabaseError
from ...model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginNetworkException, QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.resources import plugin_name
from ...qgis_plugin_tools.tools.version import version_from_string, string_from_version
from ...ui.db_tools_ask_credentials import DbAskCredentialsDialog

LOGGER = logging.getLogger(plugin_name())


# noinspection SqlResolve
class DatabaseInitializer:

    def __init__(self, dialog: QDialog, qgs_app: QCoreApplication) -> None:
        self.dlg = dialog
        self.qgs_app = qgs_app

        self.database: Optional[Database] = None
        self.conn_params: Dict = {}
        self.plan_enum: Optional[LandUsePlanEnum] = None
        self.plan: Optional[LandUsePlan] = None

    def initialize_database(self, db_conn_name: str, plan_sting: str) -> None:
        """
        Initialize database for the land use planning
        :return:
        """
        self.register_database(db_conn_name, plan_sting)

        try:
            schema_query = self.plan.fetch_schema()

            try:
                project_query = self.plan.fetch_project(self.conn_params, db_conn_name)
            except (QgsPluginNotImplementedException, QgsPluginNetworkException):
                LOGGER.warning(tr("Not implemented:"), extra=bar_msg(tr(u"Project SQL is not implemented yet")))
                project_query = 'SELECT 1'

        except QgsPluginNetworkException as e:
            raise QgsPluginNetworkException(tr(u"Network error"), bar_msg=bar_msg(
                tr(u"Could not load schema for the plan. Check your internet connection. Details: ") + str(
                    e)))

        try:
            # Actual insertion of the schema
            self.database.execute_insert(schema_query)
        except psycopg2.OperationalError:
            raise QaavaDatabaseError(tr('Connection error'),
                                     bar_msg(tr('Could not connect to the database {} ', db_conn_name)))
        except (Exception, psycopg2.DatabaseError) as e:
            raise QaavaDatabaseError(tr('Error occured while injecting schema'),
                                     bar_msg(tr(
                                         'Check log file for details. There might be errors in schema. If the problem persists, '
                                         'contact developers')))

        try:
            # Actual insertion of project
            self.database.execute_insert(project_query)
        except psycopg2.OperationalError:
            raise QaavaDatabaseError(tr('Connection error'),
                                     bar_msg(tr('Could not connect to the database {} ', db_conn_name)))
        except (Exception, psycopg2.DatabaseError) as e:
            raise QaavaDatabaseError(tr('Error occured while inserting the project'),
                                     bar_msg(tr(
                                         'Check log file for derails. If the problem persists, '
                                         'contact developers')))

    def register_database(self, db_conn_name: str, plan_sting: str) -> None:
        """
        Register database for the land use planning
        """
        self.plan_enum = LandUsePlanEnum[plan_sting]
        self.plan: LandUsePlan = self.plan_enum.value()  # intance of plan class because of ()

        set_qaava_connection(self.plan_enum, db_conn_name)
        self.conn_params = get_db_connection_params(self.plan_enum)

        # Ask username and password if needed
        if self.conn_params["user"] is None or self.conn_params["password"] is None:
            ask_credentials_dlg = DbAskCredentialsDialog(self.conn_params["user"], self.conn_params["password"])
            result = ask_credentials_dlg.exec_()
            if result:
                self.conn_params["user"] = ask_credentials_dlg.userLineEdit.text()
                self.conn_params["password"] = ask_credentials_dlg.pwdLineEdit.text()
            else:
                raise QaavaInitializationCancelled(tr(u"Canceling"), bar_msg=bar_msg(
                    tr(u"Could not continue initializing without username and password")))
        # Save credentials to auth config
        set_auth_cfg(self.plan_enum, db_conn_name, self.conn_params["user"], self.conn_params["password"])
        self.database = Database(self.conn_params)

        if not self.database.is_valid():
            raise QaavaDatabaseError(tr(u"Database connection error"),
                                     bar_msg=bar_msg(tr(u"Could not access the database.")))

    def promote_database(self):
        """
        Promote database to newest schema version
        """
        current_version, newest_version = (version_from_string(v) for v in self.get_versions())

        if current_version < newest_version:
            try:
                migration_script = self.plan.create_migration_script(current_version)
                migration_script += 'UPDATE koodistot.tietomalli_metatiedot SET versio = %(newest_version)s'
                self.database.execute_insert(migration_script,
                                             {'newest_version': string_from_version(self.plan.newest_version)})

            except (Exception, psycopg2.DatabaseError) as e:
                LOGGER.exception('Error occurred while running migration script')
                raise QaavaDatabaseError(tr('Error occurred while running migration script'),
                                         bar_msg(tr('Please check internet connection and contact '
                                                    'developers if the problem persists')))

        LOGGER.info('Schema is up to date')

    def get_versions(self) -> Tuple[str, str]:
        """
        Get current and newest versions as string
        :return: current version of the schema and newest version of the schema
        """
        try:
            query = 'SELECT versio FROM koodistot.tietomalli_metatiedot'
            current_version = max([version_from_string(v[0]) for v in
                                   self.database.execute_select(query)])
            LOGGER.debug(f'Database version is {current_version}')
        except psycopg2.OperationalError:
            raise QaavaDatabaseError(tr('Connection error'),
                                     bar_msg(tr(u'Could not connect to the database')))
        except psycopg2.DatabaseError:
            raise QaavaDatabaseError(tr('The database is not initialized properly'),
                                     bar_msg(tr('Please initialize the database')))
        return string_from_version(current_version), string_from_version(self.plan.newest_version)

    def get_available_projects(self) -> List[str]:
        """
        Get available projects from the database
        :return:
        """
        # TODO: Move to more appropriate place?
        try:
            # noinspection SqlResolve
            query = 'SELECT name FROM qgis_projects'
            available_projects = self.database.execute_select(query)
        except psycopg2.DatabaseError:
            LOGGER.warning(tr(u"No projects available:"),
                           extra=bar_msg(tr(u"No projects found from the database")))
            available_projects = []
        return [proj[0] for proj in available_projects]
