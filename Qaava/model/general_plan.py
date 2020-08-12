import sys

from psycopg2 import sql

from .common import DatabaseTable, DbRelation, ProcessInfo
from .land_use_plan import GeneralLandUsePlan

if sys.version_info >= (3, 8):
    pass
else:
    pass


class ZoningPlan(DatabaseTable):
    schema = GeneralLandUsePlan.Schema.ZONING_PLAN.value
    _table = 'yleiskaava'
    geom = sql.Identifier('geom')
    name = sql.Identifier('nimi')
    editor = sql.Identifier('laatija')
    start_date = sql.Identifier('voimaantulopvm')

    # relations
    process_info = DbRelation(ProcessInfo, 'gid_vaihetieto')
