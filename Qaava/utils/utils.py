from typing import Union

from PyQt5.QtCore import QVariant


def parse_value(value: Union[QVariant, str]) -> Union[None, str, bool]:
    """
    Parse QSettings value
    :param value: QVariant
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
