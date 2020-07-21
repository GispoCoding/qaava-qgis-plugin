import pytest

from ..model.land_use_plan import DetailedLandUsePlan
from ..qgis_plugin_tools.tools.resources import plugin_name, plugin_path
from ..utils.constants import DETAILED_PLAN_DATA_MODEL_URL
from ..utils.exceptions import QaavaNetworkException
from ..utils.network import fetch


def test_fetch(new_project):
    data_model = fetch(DETAILED_PLAN_DATA_MODEL_URL)
    assert len(data_model) > 10000


def test_fetch_invalid_url(new_project):
    with pytest.raises(QaavaNetworkException):
        fetch("invalidurl")


def test_detailed_plan_schema_fetch(new_project):
    plan = DetailedLandUsePlan()
    schema = plan.fetch_schema()
    assert len(schema) > 1000
