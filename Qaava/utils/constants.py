IDENTIFIER = "Qaava"
QAAVA = "/Qaava"

# Urls
QAAVA_GITHUB_URL = "https://raw.githubusercontent.com/GispoCoding/qaava"

CITY_PLAN_DATA_MODEL_URL = f"{QAAVA_GITHUB_URL}/master/asemakaavan-tietomalli/tietomalli_luonnos.sql"

ENCODING = "utf-8"

# Logging
DEFAULT_LOGGING_LEVEL = "DEBUG"
DEFAULT_LOGGING_FILE_LEVEL = "INFO"

# Database
PG_CONNECTIONS = "PostgreSQL/connections"
QAAVA_DB_NAME = f"{QAAVA}/postgresqlConnectionName"

QGS_SETTINGS_PSYCOPG2_PARAM_MAP = {
    'database': 'dbname',
    'host': 'host',
    'password': 'password',
    'port': 'port',
    'username': 'user'
}
