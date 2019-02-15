# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
"""Converters for :class:`SpecificationModel`s
"""
from spawn.util.validation import validate_type

from .specification import SpecificationModel, SpecificationNode, SpecificationMetadata, IndexedNode

class SpecificationConverter:
    """Abstract base class for converting :class:`SpecificationModel`
    """
    def convert(self, spec):
        """Converts the given spec model

        :param spec: The specification model to convert
        :type spec: :class:`SpecificationModel`
        """
        raise NotImplementedError()

class DictSpecificationConverter(SpecificationConverter):
    """Class for converting specification models

    Converts :class:`SpecificationModel` into :class:`dict`
    """
    def convert(self, spec):
        """Converts the given spec model into a ``dict``

        :param spec: The specification model to convert
        :type spec: :class:`SpecificationModel`

        :returns: A ``dict`` represenation of the specification model
        :rtype: ``dict``
        """
        validate_type(spec, SpecificationModel, 'spec')
        return {
            'base_file': spec.base_file,
            'metadata': self._convert_metadata(spec.metadata),
            'spec': sum([self._convert_node(c) for c in spec.root_node.children], [])
        }

    @staticmethod
    def _convert_metadata(metadata):
        validate_type(metadata, SpecificationMetadata, 'metadata')
        return {
            'creation_time': metadata.creation_time,
            'notes': metadata.notes
        }

    def _convert_node(self, node):
        validate_type(node, SpecificationNode, 'node')
        if not node.has_property:
            return sum([self._convert_node(c) for c in node.children], [])
        node_dict = {
            'name': node.property_name,
            'value': node.property_value
        }
        if isinstance(node, IndexedNode):
            node_dict['index'] = node.index
        if node.children:
            children = []
            for child_node in node.children:
                next_children = self._convert_node(child_node)
                children += next_children
            node_dict['children'] = children
        else:
            node_dict['path'] = node.path
            if node.ghosts:
                node_dict['ghosts'] = node.ghosts
        return [node_dict]
