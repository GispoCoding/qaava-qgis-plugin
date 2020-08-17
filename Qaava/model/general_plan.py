import enum

from PyQt5.QtCore import QVariant

from .common import DatabaseTable, DbRelation, ProcessInfo, DatabaseField


class Schema(enum.Enum):
    ZONING_PLAN = 'yleiskaava'


class ZoningPlan(DatabaseTable):
    schema = Schema.ZONING_PLAN.value
    _table = 'yleiskaava'
    geom = DatabaseField('geom')
    name = DatabaseField('nimi')
    editor = DatabaseField('laatija')
    start_date = DatabaseField('voimaantulopvm', QVariant.Date)

    # relations
    process_info = DbRelation(ProcessInfo, 'gid_vaihetieto')
