import os

import pytest

import psycopg2


def is_responsive(url):
    succeeds = False
    try:
        with(psycopg2.connect(url)) as conn:
            succeeds = True
    except psycopg2.OperationalError as e:
        pass
    return succeeds


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig) -> str:
    """ Points to test docker-compose file"""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.yml")


@pytest.fixture(scope="session")
def database_params() -> {str: str}:
    params = {"dbname": "qaavadb1", "user": "postgres", "host": "localhost", "password": "postgres", "port": "5439"}
    return params


@pytest.fixture(scope='session')
def docker_database(docker_ip, docker_services, database_params) -> {str: {str: str}}:
    """

    :param docker_ip: pytest-docker fixture
    :param docker_services:  pytest-docker fixture
    :return: db urls and params in a dict
    """
    port = docker_services.port_for("qaava-test-db", 5432)
    params = {**database_params, **{"port": port}}
    url = "dbname={dbname} user={user} host={host} password={password} port={port}".format(**params)
    params2 = {**params, **{"dbname": "qaavadb2"}}
    url2 = "dbname={dbname} user={user} host={host} password={password} port={port}".format(**params2)
    docker_services.wait_until_responsive(
        timeout=10.0, pause=1, check=lambda: is_responsive(url)
    )
    return {
        "db1": {"url": url, **params},
        "db2": {"url": url2, **params2}
    }
