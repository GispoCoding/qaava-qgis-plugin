import enum

from PyQt5.QtCore import QVariant

from .common import DatabaseTable, DbRelation, ProcessInfo, DatabaseField


class Schema(enum.Enum):
    PLAN = 'asemakaavat'


class DetailedPlan(DatabaseTable):
    schema = Schema.PLAN.value
    _table = 'asemakaava'
    geom = DatabaseField('geom')
    name = DatabaseField('nimi')
    editor = DatabaseField('laatija')
    start_date = DatabaseField('voimaantulopvm', QVariant.Date)

    # relations
    process_info = DbRelation(ProcessInfo, 'gid_vaihetieto')
