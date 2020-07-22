import logging
import webbrowser

from .base_panel import BasePanel
from ..definitions.qui import Panels
from ..qgis_plugin_tools.tools.custom_logging import get_log_level_key, LogTarget, get_log_level_name
from ..qgis_plugin_tools.tools.resources import plugin_name, plugin_path
from ..qgis_plugin_tools.tools.settings import set_setting

LOGGER = logging.getLogger(plugin_name())

LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class SettingsPanel(BasePanel):

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Database

    def setup_panel(self):
        self.dlg.combo_box_log_level_file.clear()
        self.dlg.combo_box_log_level_console.clear()
        self.dlg.combo_box_log_level_file.addItems(LOGGING_LEVELS)
        self.dlg.combo_box_log_level_console.addItems(LOGGING_LEVELS)
        self.dlg.combo_box_log_level_file.setCurrentText(get_log_level_name(LogTarget.FILE))
        self.dlg.combo_box_log_level_console.setCurrentText(get_log_level_name(LogTarget.STREAM))

        self.dlg.combo_box_log_level_file.currentTextChanged.connect(
            lambda level: set_setting(get_log_level_key(LogTarget.FILE), level))

        self.dlg.combo_box_log_level_console.currentTextChanged.connect(
            lambda level: set_setting(get_log_level_key(LogTarget.STREAM), level))

        self.dlg.btn_open_log.clicked.connect(lambda _: webbrowser.open(plugin_path("logs", f"{plugin_name()}.log")))
