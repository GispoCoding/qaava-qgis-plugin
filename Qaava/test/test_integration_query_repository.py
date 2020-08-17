from ..core.db.querier import Querier
from ..core.db.query_repository import QueryRepository
from ..definitions.db import Operation
from ..model.common import ProcessInfo
from ..model.general_plan import ZoningPlan
from ..model.land_use_plan import LandUsePlanEnum


def test_fetch_available_status_codes(general_db):
    repository = QueryRepository(general_db, LandUsePlanEnum.general)
    codes = repository.fetch_available_status_codes()
    assert len(codes) == 9
    assert {'gid': 1, 'name': 'aloitusvaihe'} in codes


def test_querier_fields():
    querier = Querier(LandUsePlanEnum.general.name)
    assert querier.fields == {'laatija': ZoningPlan.editor, 'nimi': ZoningPlan.name,
                              'voimaantulopvm': ZoningPlan.start_date, 'vaihetieto.nimi': ProcessInfo.name}


def test_fetch_land_use_with_status(general_db):
    # TODO: add test data
    repository = QueryRepository(general_db, LandUsePlanEnum.general)
    repository.set_status(1, Operation.EQ)
    plans = repository.run_query()
    assert len(plans) == 0


def test_query_repository_initialization(general_db):
    repository = QueryRepository(general_db, LandUsePlanEnum.general)
    query = repository.show_query()
    assert query == 'SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl '


def test_query_repository_initialization_detailed(general_db):
    repository = QueryRepository(general_db, LandUsePlanEnum.detailed)
    query = repository.show_query()
    assert query == 'SELECT pl."gid" FROM "asemakaavat"."asemakaava" pl '


def test_query_status_1(general_db):
    repository = QueryRepository(general_db, LandUsePlanEnum.general)
    repository.set_status(1, Operation.EQ)
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE p."gid"=1')


def test_query_status_2(general_db):
    repository = QueryRepository(general_db, LandUsePlanEnum.general)
    repository.add_and_condition(ProcessInfo.name, Operation.GT, "1: aloitusvaihe")
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE p."gid">1')


def test_query_chained_1(general_db):
    repository = QueryRepository(general_db, LandUsePlanEnum.general)
    repository.add_and_condition(ZoningPlan.name, Operation.EQ, "testplan")
    repository.add_and_condition(ZoningPlan.editor, Operation.LIKE, "ed%or")
    repository.add_and_condition(ProcessInfo.name, Operation.EQ, "1: aloitusvaihe")
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "yleiskaava"."yleiskaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE '
                     'pl."nimi"=\'testplan\' AND  pl."laatija" LIKE \'ed%or\' AND  p."gid"=1')
