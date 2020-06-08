import logging
import os
from logging.handlers import RotatingFileHandler

from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgisInterface

from .constants import (IDENTIFIER, DEFAULT_LOGGING_LEVEL, DEFAULT_LOGGING_FILE_LEVEL)


def _create_logger() -> logging.Logger:
    logger = logging.getLogger(IDENTIFIER)
    lvl = logging.getLevelName(DEFAULT_LOGGING_LEVEL)
    logger.setLevel(lvl)

    if len(logger.handlers) < 2:
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)-7s]: %(message)s", "%d.%m.%Y %H:%M:%S")
        file_handler = RotatingFileHandler(os.path.join(os.path.dirname(__file__), "../logs/qaava.log"),
                                           maxBytes=1024 * 1024 * 2)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.getLevelName(DEFAULT_LOGGING_FILE_LEVEL))

        # TODO: stream handler can maybe be removed at certain point of development
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(lvl)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger


LOGGER = _create_logger()


def debug(msg: str, *args, **kwargs) -> None:
    LOGGER.debug(msg, *args, **kwargs)


def msg_info(iface: QgisInterface, msg: str, details="", duration=4) -> None:
    info(f"{msg}: {details}")
    iface.messageBar().pushMessage(title=msg, text=details, level=Qgis.Info, duration=duration)


def info(msg: str, *args, **kwargs) -> None:
    QgsMessageLog.logMessage(msg, IDENTIFIER, Qgis.Info)
    LOGGER.info(msg, *args, **kwargs)


def msg_warn(iface: QgisInterface, msg: str, details="", duration=6) -> None:
    warning(f"{msg}: {details}")
    iface.messageBar().pushMessage(title=msg, text=details, level=Qgis.Warning, duration=duration)


def warning(msg: str, *args, **kwargs) -> None:
    QgsMessageLog.logMessage(msg, IDENTIFIER, Qgis.Warning)
    LOGGER.warning(msg, *args, **kwargs)


def msg_error(iface: QgisInterface, msg: str, details="", duration=10) -> None:
    exception(f"{msg}: {details}")
    iface.messageBar().pushMessage(title=msg, text=details, level=Qgis.Critical, duration=duration)


def error(msg: str, *args, **kwargs) -> None:
    QgsMessageLog.logMessage(msg, IDENTIFIER, Qgis.Critical)
    LOGGER.error(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    QgsMessageLog.logMessage(msg, IDENTIFIER, Qgis.Critical)
    LOGGER.exception(msg, *args, **kwargs)
