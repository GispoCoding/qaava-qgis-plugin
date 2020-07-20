import logging

from PyQt5.QtCore import QSettings, QUrl
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import Qgis, QgsBlockingNetworkRequest

from .constants import IDENTIFIER, ENCODING
from .exceptions import QaavaNetworkException
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


def fetch(url: str) -> str:
    """
    Fetch resource from the internet. Similar to requests.get(url) but is
    recommended way of handling requests in QGIS plugin
    :param url: address of the web resource
    :return: encoded string of the content
    """
    LOGGER.debug(url)
    req = QNetworkRequest(QUrl(url))

    # http://osgeo-org.1560.x6.nabble.com/QGIS-Developer-Do-we-have-a-User-Agent-string-for-QGIS-td5360740.html
    user_agent = QSettings().value("/qgis/networkAndProxy/userAgent", "Mozilla/5.0")
    user_agent += " " if len(user_agent) else ""
    # noinspection PyUnresolvedReferences
    user_agent += f"QGIS/{Qgis.QGIS_VERSION_INT}"
    user_agent += f" {IDENTIFIER}"
    # https://www.riverbankcomputing.com/pipermail/pyqt/2016-May/037514.html
    req.setRawHeader(b"User-Agent", bytes(user_agent, ENCODING))

    request_blocking = QgsBlockingNetworkRequest()
    _ = request_blocking.get(req)
    reply = request_blocking.reply()
    reply_error = reply.error()
    if reply_error != QNetworkReply.NoError:
        raise QaavaNetworkException(tr('Request failed') + ':\n\n' + reply.errorString())

    return bytes(reply.content()).decode(ENCODING)
