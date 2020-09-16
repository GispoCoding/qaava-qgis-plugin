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

import logging
import uuid
from typing import Dict, Optional, List

from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QGridLayout, QComboBox, QPushButton, QCheckBox
from qgis.core import QgsApplication, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsProviderRegistry, QgsProject
from qgis.gui import QgsMapCanvas, QgsExtentGroupBox

from .base_panel import BasePanel
from ..core.db.querier import Querier
from ..core.exceptions import QaavaLayerError
from ..core.wrappers.field_wrapper import FieldWrapper
from ..definitions.db import Operation
from ..definitions.qui import Panels, Settings
from ..model.land_use_plan import LandUsePlanEnum
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.decorations import log_if_fails
from ..qgis_plugin_tools.tools.fields import widget_for_field, value_for_widget
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..qgis_plugin_tools.tools.settings import get_setting

LOGGER = logging.getLogger(plugin_name())


class QueryPanel(BasePanel):

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.About
        self.grid: QGridLayout = self.dlg.query_grid
        self.querier: Optional[Querier] = None
        self.rows: Dict = {}

    def setup_panel(self):
        # noinspection PyArgumentList
        change_layer = lambda _=None: self._change_layer(self.dlg.q_combo_box_layer.currentLayer())

        # noinspection PyCallByClass,PyArgumentList
        self.dlg.q_push_button_add_row.setIcon(QgsApplication.getThemeIcon('/mActionAdd.svg'))
        self.dlg.q_push_button_add_row.clicked.connect(lambda _: self._add_row(len(self.rows) + 1))
        self.dlg.q_push_button_show_query.clicked.connect(lambda _: self.run('_show_query'))
        self.dlg.q_push_button_run_query.clicked.connect(self.run)
        self.dlg.q_push_button_clear_filter.clicked.connect(self._clear_filter)

        # noinspection PyArgumentList
        self.dlg.q_combo_box_layer.setExcludedProviders(
            [p for p in QgsProviderRegistry.instance().providerList() if p != 'postgres'])

        # noinspection PyArgumentList
        QgsProject.instance().layersAdded.connect(self._updated_map_layers)

        self.dlg.q_push_button_reset.clicked.connect(change_layer)
        self.dlg.q_push_button_refresh.clicked.connect(change_layer)
        self.dlg.q_combo_box_layer.layerChanged.connect(change_layer)

        if self.dlg.q_combo_box_layer.currentLayer() is not None:
            change_layer()

    def teardown_panel(self):
        self._clear_filter()

    @log_if_fails
    def _initialize(self, crs: Optional[QgsCoordinateReferenceSystem] = None):
        # this is also called upon self.setup_panel by self._change_layer
        canvas: QgsMapCanvas = self.dlg.iface.mapCanvas()
        crs = crs if crs is not None else canvas.mapSettings().destinationCrs()
        extent_gb: QgsExtentGroupBox = self.dlg.q_extent
        extent_gb.setOriginalExtent(canvas.extent(), crs)
        extent_gb.setCurrentExtent(canvas.extent(), crs)
        extent_gb.setOutputCrs(crs)
        extent_gb.setMapCanvas(canvas)

        for row_id in list(self.rows.keys()):
            self._remove_row(row_id)

        # noinspection PyArgumentList
        self._updated_map_layers(QgsProject.instance().mapLayers().values())

    def _updated_map_layers(self, map_layers: List[QgsVectorLayer]):
        excepted_layers = self.dlg.q_combo_box_layer.exceptedLayerList()
        excepted_strings = get_setting(Settings.layer_should_not_contain_string.name,
                                       Settings.layer_should_not_contain_string.value,
                                       str).split(',')

        for layer in map_layers:
            if any(x in layer.name() for x in excepted_strings):
                excepted_layers.append(layer)
        self.dlg.q_combo_box_layer.setExceptedLayerList(excepted_layers)

    def _change_layer(self, layer: Optional[QgsVectorLayer]):
        self.dlg.q_text_browser_sql.setText('')
        self.dlg.q_gb_sql.setCollapsed(True)
        self._clear_filter()
        if layer is not None:
            # Set extent disabled if layer has no geometry
            self.dlg.q_extent.setEnabled(layer.geometryType() != 4)

            try:
                # TODO: get the plan from elsewhere
                self.querier = Querier(LandUsePlanEnum.general.name, layer,
                                       limit_for_unique=int(
                                           get_setting(Settings.number_of_query_choices.name,
                                                       Settings.number_of_query_choices.value,
                                                       int)))
            except QaavaLayerError as e:
                LOGGER.error(str(e), extra=e.bar_msg)
            self._initialize(crs=layer.crs())

    def _run(self):
        self._generate_query()
        relevant_ids = self.querier.run()
        if len(relevant_ids):
            LOGGER.info(tr('Filtering layer {}', self.querier.layer_wrapper.layer_name),
                        extra=bar_msg(tr(
                            'Showing {} features. Keep this window open to see filtered, close the dialog '
                            'of press Clear to clear filter.',
                            len(relevant_ids)), duration=8, success=True))
            self.querier.set_filter(relevant_ids)
        else:
            LOGGER.info(tr('The query did not result any features'), extra=bar_msg())

    def _show_query(self):
        self._generate_query()
        query = str(self.querier.show_query())
        self.dlg.q_gb_sql.setCollapsed(False)
        self.dlg.q_text_browser_sql.setText(query)

    def _clear_filter(self):
        if self.querier is not None:
            LOGGER.debug('Clearing filter')
            self.querier.clear_filter()

    def _generate_query(self):
        self.querier.clear()
        for row in self.rows.values():
            field = self.querier.fields[row['field'].currentText()]
            operation = Operation(row['operation'].currentText())
            value = value_for_widget(row['value'])

            self.querier.add_condition(field, operation, value)

        if self.dlg.q_extent.isChecked():
            self.querier.add_extent(self.dlg.q_extent.outputExtent())

    @log_if_fails
    # noinspection PyCallByClass,PyArgumentList,PyUnresolvedReferences
    def _add_row(self, row_index: int):
        if self.querier is None:
            LOGGER.debug("Won't add row since querier is not initialzied")
            return

        bx_field = QComboBox()
        bx_operation = QComboBox()
        bx_operation.addItems([op.value for op in Operation])
        bx_operation.setCurrentText(Operation.EQ.value)
        bx_value = QComboBox()
        bx_value.setEditable(True)

        row_uuid = str(uuid.uuid4())
        row = {
            'field': bx_field,
            'operation': bx_operation,
            'value': bx_value,
        }
        self.rows[row_uuid] = row
        self.grid.addWidget(bx_field, row_index, 1)
        self.grid.addWidget(bx_operation, row_index, 2)
        self.grid.addWidget(bx_value, row_index, 3)

        # noinspection PyUnresolvedReferences
        bx_field.currentTextChanged.connect(lambda field: self._field_changed(self.querier.fields[field], row_uuid))
        bx_field.addItems(list(self.querier.fields.keys()))
        bx_field.setCurrentText(list(self.querier.fields.keys())[0])

        # noinspection PyCallByClass,PyArgumentList
        b_rm = QPushButton(text='', icon=QgsApplication.getThemeIcon('/mActionRemove.svg'))
        b_rm.setToolTip(tr('Remove row'))
        # noinspection PyUnresolvedReferences
        b_rm.clicked.connect(lambda _: self._remove_row(row_uuid))
        self.rows[row_uuid]['rm'] = b_rm
        self.grid.addWidget(b_rm, row_index, 0)

    def _field_changed(self, field: FieldWrapper, row_uuid: str):
        row = self.rows.get(row_uuid, None)
        if row is None:
            return

        self._replace_value_widget(row_uuid, field.type)
        w_value = row['value']
        bx_operation = row['operation']
        if not isinstance(w_value, QCheckBox):
            w_value.clear()

        choices, string = self.querier.fetch_choices(field)

        if len(choices) and isinstance(w_value, QComboBox):
            w_value.addItems(choices)

        bx_operation.clear()
        bx_operation.addItems(
            [op.value for op in Operation if string or op not in [Operation.LIKE, Operation.ILIKE]])

    def _remove_row(self, row_uuid: str):
        row = self.rows.pop(row_uuid)
        for widget in row.values():
            self.grid.removeWidget(widget)
            widget.hide()
            widget.setParent(None)
            widget = None

    def _replace_value_widget(self, row_uuid: str, field_type: QVariant):
        row = self.rows[row_uuid]
        old_widget = row['value']
        new_widget = widget_for_field(field_type)
        self.grid.replaceWidget(old_widget, new_widget)

        old_widget.hide()
        old_widget.setParent(None)
        old_widget = None

        row['value'] = new_widget
        return new_widget
