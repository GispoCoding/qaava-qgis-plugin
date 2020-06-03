import pytest

from ..utils.constants import CITY_PLAN_DATA_MODEL_URL
from ..utils.network import fetch

from .utilities import get_qgis_app
from ..utils.exceptions import QaavaNetworkException

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

CONN_NAME = "test_qaava_conn"


@pytest.fixture(scope='function')
def iface():
    """Runs before every test. """
    yield IFACE.newProject()


def test_fetch(iface) -> None:
    data_model = fetch(CITY_PLAN_DATA_MODEL_URL)
    assert len(data_model) > 10000


def test_fetch_invalid_url(iface) -> None:
    with pytest.raises(QaavaNetworkException):
        fetch("invalidurl")
