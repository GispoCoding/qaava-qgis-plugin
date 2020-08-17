from ..core.db.querier import Querier
from ..core.db.query_repository import QueryRepository
from ..definitions.db import Operation
from ..model.common import ProcessInfo
from ..model.land_use_plan import LandUsePlanEnum


# noinspection SqlResolve
def test_query_repository_initialization(detailed_db):
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    query = repository.show_query()
    assert query == 'SELECT pl."gid" FROM "asemakaavat"."asemakaava" pl '


def test_querier_fields():
    querier = Querier(LandUsePlanEnum.detailed.name)
    assert querier.fields == {'vaihetieto.nimi': ProcessInfo.name}


# noinspection SqlResolve
def test_query_status_1(detailed_db):
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    repository.set_status(1, Operation.EQ)
    query = repository.show_query()
    assert query == ('SELECT pl."gid" FROM "asemakaavat"."asemakaava" pl LEFT JOIN '
                     '"koodistot"."vaihetieto" p ON "gid_vaihetieto"=p."gid" WHERE p."gid"=1')


def test_fetch_available_status_codes(detailed_db):
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    codes = repository.fetch_available_status_codes()
    assert len(codes) == 8
    assert {'gid': 1, 'name': 'aloitusvaihe'} in codes


def test_fetch_land_use_with_status(detailed_db):
    # TODO: add test data
    repository = QueryRepository(detailed_db, LandUsePlanEnum.detailed)
    repository.set_status(1, Operation.EQ)
    plans = repository.run_query()
    assert len(plans) == 0
