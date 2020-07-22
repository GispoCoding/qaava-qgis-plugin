from ..qgis_plugin_tools.tools.settings import setting_key

# Urls
QAAVA_GITHUB_URL = "https://raw.githubusercontent.com/GispoCoding/qaava"

DETAILED_PLAN_DATA_MODEL_URL = f"{QAAVA_GITHUB_URL}/master/asemakaavan-tietomalli/tietomalli_luonnos.sql"

# Database
PG_CONNECTIONS = "PostgreSQL/connections"
QAAVA_DB_NAME = setting_key("postgresqlConnectionName")

QGS_SETTINGS_PSYCOPG2_PARAM_MAP = {
    'database': 'dbname',
    'host': 'host',
    'password': 'password',
    'port': 'port',
    'username': 'user'
}

QGS_DEFAULT_DB_SETTINGS = {
    'allowGeometrylessTables': 'false',
    'authcfg': '',
    'dontResolveType': 'false',
    'estimatedMetadata': 'false',
    'geometryColumnsOnly': 'false',
    'projectsInDatabase': 'false',
    'publicOnly': 'false',
    'savePassword': 'true',
    'saveUsername': 'true',
    'service': '',
    'sslmode': 'SslDisable',
}
