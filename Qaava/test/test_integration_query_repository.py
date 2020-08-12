from psycopg2 import sql

from ..core.db.query_repository import QueryRepository


def test_fetch_available_status_codes(general_db):
    repository = QueryRepository(general_db)
    codes = repository.fetch_available_status_codes()
    assert len(codes) == 9
    assert {'gid': 1, 'name': 'aloitusvaihe'} in codes


def test_fetch_available_status_codes_with_additional(general_db):
    repository = QueryRepository(general_db)
    additional_sql = sql.SQL(' WHERE gid = %(gid)s')

    codes = repository.fetch_available_status_codes(additional_sql, vars={'gid': 1})
    assert len(codes) == 1
    assert {'gid': 1, 'name': 'aloitusvaihe'} in codes


def test_fetch_land_use_with_status(general_db):
    # TODO: add test data
    repository = QueryRepository(general_db)
    plans = repository.fetch_zoning_plans_with_status(1)
    assert len(plans) == 0
