"""Definitions for GUI concepts."""

#  Gispo Ltd., hereby disclaims all copyright interest in the program Qaava-qgis-plugin
#  Copyright (C) 2020 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Qaava-qgis-plugin.
#
#  Qaava-qgis-plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Qaava-qgis-plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Qaava-qgis-plugin.  If not, see <https://www.gnu.org/licenses/>.
import enum

from PyQt5.QtGui import QIcon
from qgis.core import QgsApplication

from ..qgis_plugin_tools.tools.resources import resources_path


class Panels(enum.Enum):
    """Panels in the Dialog"""
    Query = {'icon': '/search.svg'}
    Database = {'icon': '/dbmanager.svg'}
    Settings = {'icon': '/mActionMapSettings.svg'}
    About = {'icon': '/mActionHelpContents.svg'}

    # noinspection PyCallByClass,PyArgumentList
    @property
    def icon(self) -> QIcon:
        _icon: str = self.value['icon']

        # QGIS icons
        # https://github.com/qgis/QGIS/tree/master/images/themes/default
        if _icon.startswith("/"):
            return QgsApplication.getThemeIcon(_icon)
        else:
            # Internal icons
            return QIcon(resources_path('icons', _icon))


@enum.unique
class Settings(enum.Enum):
    number_of_query_choices = 10
    layer_should_not_contain_string = 'many_,tyyppi'
