from .specification import SpecificationModel, SpecificationNode, SpecificationMetadata
from multiwindcalc.util.validation import validate_type

class SpecificationConverter:
    """Abstract base class for converting ``SpecificationModel``s

    Methods
    -------
    convert(spec)
        Converts the given spec model
    """
    def convert(self, spec):
        raise NotImplementedError()

class DictSpecificationConverter:
    """Class for converting ``SpecificationModel``s into ``dict``s

    Methods
    -------
    convert(spec)
        Converts the ``SpecificationModel`` provided into a ``dict``
    """
    def convert(self, spec):
        """Converts a ``SpecificationModel`` into a ``dict``

        Parameters
        ----------
        spec : SpecificationModel
            The specification model
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
