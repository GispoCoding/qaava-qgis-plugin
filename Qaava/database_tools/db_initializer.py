import logging

import psycopg2
from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .database import Database
from .db_utils import (set_qaava_connection, get_db_connection_params)
from .gui.db_tools_ask_credentials import DbAskCredentialsDialog
from .gui.db_tools_initializer_dialog import DbInitializerDialog
from ..model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..utils.exceptions import QaavaAuthConfigException, QaavaNetworkException, QaavaNotImplementedException

LOGGER = logging.getLogger(plugin_name())


class DatabaseInitializer:

    def __init__(self, iface: QgisInterface, qgs_app: QgsApplication) -> None:
        self.iface = iface
        self.dlg = DbInitializerDialog(iface)
        self.qgs_app = qgs_app

    def initialize_database(self) -> None:
        """
        Initialize database for the land use planning
        :return:
        """
        db_conn_name = self.dlg.get_db()
        plan_enum = LandUsePlanEnum[self.dlg.get_plan()]
        plan: LandUsePlan = plan_enum.value()  # intance of plan class because of ()

        try:
            set_qaava_connection(plan_enum, db_conn_name)
            conn_params = get_db_connection_params(plan_enum, self.qgs_app)
        except QaavaAuthConfigException as e:
            LOGGER.error(tr(u"Auth config error occurred while fetching database connection parameters:"),
                         extra=bar_msg(e))
            return
        except Exception as e:
            LOGGER.error(tr(u"Error occurred while fetching database connection parameters:"), extra=bar_msg(e))
            return

        # Ask username and password if needed
        # TODO: should these be saved using auth config?
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

        database = Database(conn_params)

        if not database.is_valid():
            LOGGER.warning(tr(u"Database connection error"),
                           extra=bar_msg(tr(u"Could not access the database.")))
            return

        try:
            schema_query = plan.fetch_schema()
        except QaavaNetworkException as e:
            LOGGER.error(tr(u"Network error:"),
                         extra=bar_msg(
                             tr(u"Could not load schema for the plan. Check your internet connection. Details: ") + str(
                                 e)))
            return
        except QaavaNotImplementedException:
            LOGGER.warning(tr(u"Not implemented:"),
                           extra=bar_msg(tr(u"Schema for the selected plan is not implemented yet")))
            return

        try:
            # Actual insertion of the schema
            database.execute_insert(schema_query)
        except psycopg2.OperationalError:
            LOGGER.error(tr(u"Connection error:"),
                         extra=bar_msg(tr(u"Could not connect to the database: ") + db_conn_name))
        except (Exception, psycopg2.DatabaseError) as e:
            LOGGER.error(tr(u"Error occurred while injecting schema:"),
                         extra=bar_msg(e))

        LOGGER.info(tr(u"Success"),
                    extra=bar_msg(tr(u"Database initialized succesfully with land use plan ") + plan_enum.name,
                                  success=True))
