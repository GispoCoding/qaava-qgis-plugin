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

from .field_wrapper import FieldWrapper, RelationalFieldWrapper
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
        return sql.Identifier(self.uri.table(), self.pk_field)

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
        # noinspection PyArgumentList
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
        # noinspection PyArgumentList
        relation_manager: QgsRelationManager = QgsProject.instance().relationManager()

        fields = []

        field: QgsField
        for idx, field in enumerate(layer.fields().toList()):
            field_name = field.name()
            if not field_name.startswith('gid_'):
                unique_values = layer.uniqueValues(idx, limit=limit) if limit > 0 else set()
                wrapper = FieldWrapper.from_layer_wrapper(self, field, idx, unique_values, self.pk_field)
                fields.append(wrapper)

            elif related_fields:
                fields += self._get_fields_related_to_field(field, idx, layer, limit, relation_manager)

        if related_fields:
            fields += self._get_related(layer, limit, relation_manager)

        return fields

    def _get_related(self, layer, limit, relation_manager) -> List[FieldWrapper]:
        fields: List[FieldWrapper] = []
        relations: List[QgsRelation] = relation_manager.referencedRelations(layer)
        relations = list(filter(lambda r: 'many_' in r.referencingLayer().name(), relations))
        if len(relations):
            for relation in relations:
                rlw = RelationalLayerWrapper.create(self, relation_manager, relation)
                fields += rlw.get_fields(limit)

        return fields

    def _get_fields_related_to_field(self, field, idx, layer, limit, relation_manager) -> List[FieldWrapper]:
        fields: List[FieldWrapper] = []
        relations: List[QgsRelation] = relation_manager.referencingRelations(layer, idx)

        if len(relations):
            for relation in relations:
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


class RelationalLayerWrapper(LayerWrapper):

    def __init__(self, layer_name: str, foreign_layer_name: str, parent_layer: LayerWrapper,
                 fw1: FieldWrapper, fw2: FieldWrapper, fw3: FieldWrapper, fw4: FieldWrapper) -> None:
        super().__init__(layer_name, parent_layer=parent_layer)
        self.foreign_layer_name = foreign_layer_name
        self.fw1 = fw1
        self.fw2 = fw2
        self.fw3 = fw3
        self.fw4 = fw4

    def _get_other_layer(self):
        """
        Get QgsVectorLayer from wrapper
        """
        # noinspection PyArgumentList
        layers = list(
            filter(lambda l: isinstance(l, QgsVectorLayer),
                   QgsProject.instance().mapLayersByName(self.foreign_layer_name)))
        if len(layers) != 1:
            raise QaavaLayerError(tr("Invalid number of layers in project"), bar_msg=bar_msg(
                tr("{} layers by the name of {}, expecting 1", len(layers), self.foreign_layer_name)))
        return layers[0]

    @staticmethod
    def create(layer_wrapper: LayerWrapper, relation_manager: QgsRelationManager,
               relation: QgsRelation) -> 'RelationalLayerWrapper':
        referencing_layer: QgsVectorLayer = relation.referencingLayer()
        referencing_field_idx = relation.referencingFields()[0]
        referencing_field: QgsField = referencing_layer.fields().toList()[referencing_field_idx]
        referenced_field_idx = relation.referencedFields()[0]
        referenced_field: QgsField = layer_wrapper.get_layer().fields().toList()[referenced_field_idx]

        try:
            other_relation: QgsRelation = [r for r in relation_manager.referencingRelations(referencing_layer)
                                           if r.id() != relation.id()][0]
        except KeyError:
            raise QaavaLayerError(tr('Relation error'), bar_msg(
                tr('Relation {} does not contain referencing another layer', relation.name())))

        other_layer: QgsVectorLayer = other_relation.referencedLayer()
        other_layer_field_idx = other_relation.referencedFields()[0]
        other_layer_field = other_layer.fields().toList()[other_layer_field_idx]
        idxxx = other_relation.referencingFields()[0]
        flddd = referencing_layer.fields().toList()[idxxx]

        relation_layer_wrapper = LayerWrapper.from_qgs_layer(referencing_layer)

        rf_fw1 = FieldWrapper.from_layer_wrapper(relation_layer_wrapper, referencing_field, referenced_field_idx, set(),
                                                 '')
        rf_fw2 = FieldWrapper.from_layer_wrapper(layer_wrapper, referenced_field, referencing_field_idx, set(), '')
        rf_fw3 = FieldWrapper.from_layer_wrapper(relation_layer_wrapper, flddd, idxxx, set(), '')
        other_layer_wrapper = LayerWrapper.from_qgs_layer(other_layer, relation_layer_wrapper, rf_fw3)

        rf_fw4 = FieldWrapper.from_layer_wrapper(other_layer_wrapper, other_layer_field, other_layer_field_idx, set(),
                                                 '')

        return RelationalLayerWrapper(referencing_layer.name(), other_layer.name(), layer_wrapper, rf_fw1,
                                      rf_fw2, rf_fw3, rf_fw4)

    def get_fields(self, limit: int, related_fields: bool = False) -> List[RelationalFieldWrapper]:
        layer = self._get_other_layer()
        lw = LayerWrapper.from_qgs_layer(layer, self.parent_layer)
        fields = []

        field: QgsField
        for idx, field in enumerate(layer.fields().toList()):
            field_name = field.name()
            if not field_name.startswith('gid_'):
                unique_values = layer.uniqueValues(idx, limit=limit) if limit > 0 else set()
                wrapper = RelationalFieldWrapper.from_relation_wrapper(self, lw, field, idx, unique_values)
                fields.append(wrapper)

        return fields
