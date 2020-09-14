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
from typing import List, Optional, Union

from psycopg2 import sql
from psycopg2.sql import Composable
from qgis.core import (QgsVectorLayer, QgsProject, QgsField, QgsRelationManager, QgsRelation, QgsDataSourceUri)

from .field_wrapper import FieldWrapper
from ..exceptions import QaavaLayerError
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class LayerWrapper:

    def __init__(self, layer_name: str, primary_key_field: Optional[str] = None,
                 parent_layer: Optional['LayerWrapper'] = None, foreign_field: Optional[FieldWrapper] = None) -> None:
        self.layer_name = layer_name
        self.pk_field = primary_key_field
        self.parent_layer = parent_layer
        self.foreign_field = foreign_field

    @staticmethod
    def from_qgs_layer(layer: QgsVectorLayer, parent_layer: Optional['LayerWrapper'] = None,
                       foreign_field: Optional[FieldWrapper] = None) -> 'LayerWrapper':
        pk_idxs = layer.primaryKeyAttributes()
        if len(pk_idxs):
            pk_field = layer.fields().toList()[pk_idxs[0]].name()
        else:
            pk_field = None
        return LayerWrapper(layer.name(), pk_field, parent_layer=parent_layer, foreign_field=foreign_field)

    @property
    def uri(self) -> QgsDataSourceUri:
        return self.get_layer().dataProvider().uri()

    @property
    def pk(self) -> Composable:
        return sql.Identifier(self.pk_field)

    @property
    def geom_field(self) -> Composable:
        return sql.Identifier(self.uri.geometryColumn())

    @property
    def table(self) -> Composable:
        uri = self.uri
        return sql.Identifier(uri.schema(), uri.table())

    def get_layer(self) -> QgsVectorLayer:
        """
        Get QgsVectorLayer from wrapper
        """
        layers = list(
            filter(lambda l: isinstance(l, QgsVectorLayer),
                   QgsProject.instance().mapLayersByName(self.layer_name)))
        if len(layers) != 1:
            raise QaavaLayerError(tr("Invalid number of layers in project"), bar_msg=bar_msg(
                tr("{} layers by the name of {}, expecting 1", len(layers), self.layer_name)))
        return layers[0]

    def get_fields(self, limit: int, related_fields: bool = True) -> List[FieldWrapper]:
        """
        Get fields as list of FieldWrappers
        :param limit: How many unique values are fetched
        :param related_fields: Whether to list also fields from relations
        """
        layer = self.get_layer()
        relation_manager: QgsRelationManager = QgsProject.instance().relationManager()

        fields = []

        field: QgsField
        for idx, field in enumerate(layer.fields().toList()):
            field_name = field.name()
            if not field_name.startswith('gid_') and not (
                field_name == self.pk_field and self.parent_layer is not None):
                unique_values = layer.uniqueValues(idx, limit=limit) if limit > 0 else set()
                wrapper = FieldWrapper.from_layer_wrapper(self, field, idx, unique_values, self.pk_field)
                fields.append(wrapper)

            elif related_fields:
                relations: List[QgsRelation] = relation_manager.referencingRelations(layer, idx)
                if len(relations) >= 1:
                    relation = relations[0]
                    referenced_layer: QgsVectorLayer = relation.referencedLayer()
                    ref_field_idx = relation.referencedFields()[0]
                    ref_field: QgsField = referenced_layer.fields().toList()[ref_field_idx]
                    fld_wrapper = FieldWrapper.from_layer_wrapper(self, field, idx, set(), ref_field.name())
                    ref_layer = LayerWrapper.from_qgs_layer(referenced_layer, self, fld_wrapper)
                    fields += ref_layer.get_fields(limit, False)

        return fields

    def set_filter(self, ids: List[Union[int, str]]) -> bool:
        if self.pk_field is None:
            LOGGER.warning(f"Primary field is not set for the layer {self.layer_name}")
            return False
        if len(ids):
            layer = self.get_layer()
            if isinstance(ids[0], str):
                ids_str = '\',\''.join(ids)
                ids_str = f'\'{ids_str}\''
            else:
                ids_str = ','.join(map(str, ids))
            query = f'{self.pk_field} IN ({ids_str})'
            LOGGER.debug(query)
            return layer.setSubsetString(query)
        else:
            self.clear_filter()

    def clear_filter(self) -> bool:
        layer = self.get_layer()
        return layer.setSubsetString('')
