"""Converters for :class:`SpecificationModel`s
"""
from .specification import SpecificationModel, SpecificationNode, SpecificationMetadata
from multiwindcalc.util.validation import validate_type

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
            'spec': [self._convert_node(c) for c in spec.root_node.children]
        }
    
    def _convert_metadata(self, metadata):
        validate_type(metadata, SpecificationMetadata, 'metadata')
        return {
            'creation_time': metadata.creation_time,
            'notes': metadata.notes
        }
    
    def _convert_node(self, node):
        validate_type(node, SpecificationNode, 'node')
        node_dict = {
            'name': node.property_name,
            'value': node.property_value
        }
        if node.children:
            node_dict['children'] = [self._convert_node(c) for c in node.children]
        else:
            node_dict['path'] = node.path
        return node_dict
