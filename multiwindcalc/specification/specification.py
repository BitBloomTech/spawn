"""Classes describing the specification
"""
from copy import deepcopy

from multiwindcalc.util import PathBuilder
from multiwindcalc.util.validation import validate_type

from .value_proxy import ValueProxy, evaluate

class SpecificationModel:
    """Class to contain the description of the :mod:`multiwindcalc` specification
    """
    def __init__(self, base_file, root_node, metadata):
        """Initialises :class:`SpecificationModel`

        :param base_file: The base file for the specification
        :type base_file: path-like
        :param root_node: The root node of the specifiction model
        :type root_node: :class:`SpecificationNode`
        :param metadata: Metadata for the specification model.
        :type metadata: :class:`SpecificationMetadata`
        """
        self._base_file = base_file
        self._root_node = root_node
        self._metadata = metadata

    @property
    def base_file(self):
        """The base file
        """
        return self._base_file
    
    @property
    def root_node(self):
        """The root node
        """
        return self._root_node
    
    @property
    def metadata(self):
        """The metadata
        """
        return self._metadata

class SpecificationMetadata:
    """Container class for the :class:`SpecificationModel` metadata
    """
    def __init__(self, type, creation_time, notes):
        """Initialises :class:`SpecificationMetadata`

        :param type: The type of specification
        :type type: str
        :param creation_time: The creation time of the specification model
        :type creation_time: :class:`datetime`
        :param notes: Any notes related to the specification model
        :type notes: str
        """
        self._type = type
        self._creation_time = creation_time
        self._notes = notes

    @property
    def type(self):
        """The type of this specification
        """
        return self._type
    
    @property
    def creation_time(self):
        """The creation time
        """
        return self._creation_time
    
    @property
    def notes(self):
        """Notes related to the specification model
        """
        return self._notes

class SpecificationNode:
    """Tree node representation of the nodes of the specification
    """
    def __init__(self, parent, property_name, property_value, path):
        """Initialses :class:`SpecificationNode`

        :param parent: The parent of this specification node.
        :type parent: :class:`SpecificationNode`
        :param property_name: The property name for this node
        :type property_name: str
        :param property_value: The property value for this node
        :type property_value: object
        :param path: The path to this specification node
        :type path: str
        """
        self._parent = parent
        self._property_name = property_name
        self._property_value = property_value
        self._children = []
        if self._parent is not None:
            self._parent.add_child(self)
        self._path_part = path
        self._collected_properties = self._collected_indices = None
        self._derived_path = None
        self._leaves = None
        self._root = None
        self._path = None

    @classmethod
    def create_root(cls, path=None):
        """Create a root node

        :param path: The path for the root node
        :type path: str

        :returns: A root specification node (without parents)
        :rtype: :class:`SpecificationNode`
        """
        return SpecificationNode(None, None, None, path)
    
    @property
    def parent(self):
        """Get the parent

        :returns: The parent node
        :rtype: :class:`SpecificationNode`
        """
        return self._parent

    @property
    def children(self):
        """Get the children of this node

        :returns: Child nodes
        :rtype: list
        """
        return self._children
    
    def add_child(self, child):
        """Adds a child to this node

        :param child: The child node to add
        :type child: :class:`SpecificationNode`
        """
        if child not in self._children:
            self._children.append(child)
            child._parent = self
    
    @property
    def leaves(self):
        """Gets the leaf nodes descended from this node

        :returns: The leaf nodes
        :rtype: list
        """
        if self._leaves is None:
            self._leaves = sum([c.leaves for c in self.children], []) if self.children else [self]
        return self._leaves
    
    @property
    def root(self):
        """Gets the root node from this node

        :returns: The root node
        :rtype: :class:`SpecificationNode`
        """
        if self._root is None:
            current_node = self
            while not current_node.is_root:
                current_node = current_node.parent
            self._root = current_node
        return self._root

    @property
    def is_root(self):
        """Is this the root node

        :returns: ``True`` if this node is the root; otherwise ``False``
        :rtype: bool
        """
        return self._parent is None

    @property
    def has_property(self):
        """Does this node have a property value

        :returns: ``True`` if this node has a type that contains properties
        :rtype: bool
        """
        return not self.is_root and type(self) == SpecificationNode
    
    @property
    def property_name(self):
        """Gets the property name for this node

        :returns: The property name
        :rtype: str
        """
        return self._property_name
    
    @property
    def property_value(self):
        """Gets the property value for this node

        :returns: The property value
        :rtype: object
        """
        return self._property_value
    
    @property
    def index(self):
        """Gets the index of this node in the parent's child nodes

        :returns: The index if this node is not a root node; otherwise -1
        :rtype: int
        """
        if self.parent is not None:
            return self.parent.children.index(self)
        return -1
    
    @property
    def collected_properties(self):
        """Gets the properties and values of this node and all ancestor nodes

        :returns: A dict containing the properties of this node and all ancestor nodes
        :rtype: dict
        """
        if self._collected_properties is None:
            properties = {}
            def _f(node):
                if node.property_value is not None:
                    properties.setdefault(node.property_name, node.property_value)
            self._climb(_f)
            self._collected_properties = properties
        return self._collected_properties
    
    @property
    def collected_indices(self):
        """Gets the property names and indicies of this node and all ancestor nodes

        :returns: A dict containing the properties of this node and all ancestor nodes
        :rtype: dict
        """
        if self._collected_indices is None:
            indices = {}
            current_node = self
            while not current_node.is_root:
                if current_node.property_value is not None:
                    indices.setdefault(current_node.property_name, current_node.index)
                current_node = current_node.parent
            self._collected_indices = indices
        return self._collected_indices
    
    @property
    def _base_path(self):
        if self._derived_path is None:
            path = PathBuilder()
            current_node = self
            while True:
                if current_node._path_part is not None:
                    path = path.join_start(current_node._path_part)
                if current_node.is_root:
                    break
                current_node = current_node.parent
            self._derived_path = str(path.format(self.collected_properties, self.collected_indices))
        return self._derived_path
    
    @property
    def path(self):
        """The path for this node.
        
        Used as a key to locate the ouputs. Evaluate using the path property and the 
        collected properties and indices at this node.

        :returns: The path for this node
        :rtype: str
        """
        if self._path is None:
            path = self._base_path
            nodes_with_matching_paths = [node for node in self.root.leaves if node._base_path == path]
            if len(nodes_with_matching_paths) > 1:
                path = str(PathBuilder(path).join(PathBuilder.index(nodes_with_matching_paths.index(self), index_format='a')))
            self._path = path
        return self._path
    
    def evaluate(self):
        """Evaluates all children in this node
        """
        for child in self._children:
            child.evaluate()
    
    def _climb(self, f):
        current_node = self
        while not current_node.is_root:
            f(current_node)
            current_node = current_node.parent

    def __repr__(self):
        properties = ', '.join('{}={}'.format(k, getattr(self, k)) for k in ['property_name', 'property_value', 'children'])
        return '{}({})'.format(type(self).__name__, properties)

class ValueProxyNode(SpecificationNode):
    def __init__(self, parent, name, value_proxy, path):
        super().__init__(parent, name, value_proxy, path)
        validate_type(value_proxy, ValueProxy, 'value_proxy')
    
    def evaluate(self):
        """Evaluates this node to determine what it's value should be.
        
        Replaces children with new values generated by this node.
        Subsequently evaluates all children.
        """
        old_children = list(self.children)
        # TODO: add ghost properties
        property_values = self.collected_properties
        values = evaluate(self._property_value, **property_values)
        self._children = [SpecificationNodeFactory().create(
            self, self.property_name, values, self._path_part, old_children
        )]
        for child in self.children:
            child.evaluate()

class DictNode(SpecificationNode):
    def __init__(self, parent, name, value, path):
        super().__init__(parent, name, value, path)
        validate_type(value, dict, 'value')
    
    def evaluate(self):
        """Evaluates this node to expand child items
        """
        node_factory = SpecificationNodeFactory()
        dict_value = deepcopy(self.property_value)
        next_name = list(dict_value.keys())[0]
        next_value = dict_value.pop(next_name)
        if dict_value:
            next_children = [node_factory.create(None, self.property_name, dict_value, self._path_part)]
        else:
            next_children = []
        new_children = [node_factory.create(self, next_name, next_value, self._path_part, next_children)]
        self._children = new_children
        for child in self.children:
            child.evaluate()
        self._property_value = None

class ListNode(SpecificationNode):
    def __init__(self, parent, name, value, path):
        super().__init__(parent, name, value, path)
        validate_type(value, list, 'value')

    def evaluate(self):
        node_factory = SpecificationNodeFactory()
        old_children = list(self.children)
        new_children = []
        for value in self.property_value:
            new_children.append(node_factory.create(self, self.property_name, value, self._path_part, old_children))
        self._children = new_children
        for child in self.children:
            child.evaluate()
        self._property_value = None

class SpecificationNodeFactory:
    def create(self, parent, name, value, path, children=[]):
        if isinstance(value, dict):
            node = DictNode(parent, name, value, path)
        elif isinstance(value, list):
            node = ListNode(parent, name, value, path)
        elif isinstance(value, ValueProxy):
            node = ValueProxyNode(parent, name, value, path)
        else:
            node = SpecificationNode(parent, name, value, path)
        for child in children:
            node.add_child(type(child)(node, child.property_name, child.property_value, child._path_part))
        return node
