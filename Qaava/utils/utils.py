from PyQt5.QtCore import QCoreApplication, QVariant
from typing import Union

from .constants import IDENTIFIER


def tr(message: str) -> str:
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate(IDENTIFIER, message)


def parse_value(value: Union[QVariant, str]) -> Union[None, str, bool]:
    """
    Parse QSettings value
    :param value: QVariant
    :return:
    """
    str_value = str(value)
    val = str_value
    if str_value == "NULL":
        val = None
    elif str_value == "true":
        val = True
    elif str_value == "false":
        val = False
    return val
