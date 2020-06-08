import psycopg2
from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from .database import Database
from .db_utils import (set_qaava_connection, get_db_connection_params)
from .gui.db_tools_ask_credentials import DbAskCredentialsDialog
from .gui.db_tools_initializer_dialog import DbInitializerDialog
from ..model.land_use_plan import LandUsePlanEnum, LandUsePlan
from ..utils import logger
from ..utils.exceptions import QaavaAuthConfigException, QaavaNetworkException, QaavaNotImplementedException
from ..utils.utils import tr


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
            logger.msg_error(self.iface,
                             tr(u"Auth config error occurred while fetching database connection parameters:"), str(e))
            return
        except Exception as e:
            logger.msg_error(self.iface, tr(u"Error occurred while fetching database connection parameters:"), str(e))
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
                logger.msg_warn(self.iface, tr(u"Canceling"),
                                tr(u"Could not continue initializing without username and password"))
                return

        database = Database(conn_params)

        if not database.is_valid():
            logger.msg_warn(self.iface, tr(u"Database connection error"), tr(u"Could not access the database."))
            return

        try:
            schema_query = plan.fetch_schema()
        except QaavaNetworkException as e:
            logger.msg_error(self.iface, tr(u"Network error:"),
                             tr(u"Could not load schema for the plan. Check your internet connection. Details: ") + str(
                                 e))
            return
        except QaavaNotImplementedException:
            logger.msg_warn(self.iface, tr(u"Not implemented:"),
                            tr(u"Schema for the selected plan is not implemented yet"))
            return

        try:
            # Actual insertion of the schema
            database.execute_insert(schema_query)
        except psycopg2.OperationalError:
            logger.msg_error(self.iface, tr(u"Connection error:"),
                             tr(u"Could not connect to the database: ") + db_conn_name)
        except (Exception, psycopg2.DatabaseError) as e:
            logger.msg_error(self.iface, tr(u"Error occurred while injecting schema:"), str(e))

        logger.msg_info(self.iface, tr(u"Success"),
                        tr(u"Database initialized succesfully with land use plan ") + plan_enum.name)
