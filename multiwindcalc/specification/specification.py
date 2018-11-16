"""Classes describing the specification
"""
from multiwindcalc.util import PathBuilder

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
    def __init__(self, parent, property_name, property_value, path, ghosts):
        """Initialses :class:`SpecificationNode`

        :param parent: The parent of this specification node.
        :type parent: :class:`SpecificationNode`
        :param property_name: The property name for this node
        :type property_name: str
        :param property_value: The property value for this node
        :type property_value: object
        :param path: The path to this specification node
        :type path: str
        :param ghosts: Ghost (non-spawner) parameters for this node
        :type ghosts: dict
        """
        self._parent = parent
        self._property_name = property_name
        self._property_value = property_value
        self._children = []
        if self._parent is not None:
            self._parent.add_child(self)
        self._path_part = path
        self._ghosts = ghosts
        self._collected_properties = self._collected_indices = self._collected_ghosts = None
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
        return SpecificationNode(None, None, None, path, {})
    
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
    def ghosts(self):
        """Returns the collected ghost parameters

        :returns: The ghost parameters for this node
        :rtype: dict
        """
        if self._collected_ghosts is None:
            ghosts = {}
            current_node = self
            while not current_node.is_root:
                # Ghosts lower down the tree supercede those higher up
                ghosts = {**current_node._ghosts, **ghosts}
                current_node = current_node.parent
            self._collected_ghosts = ghosts
        return self._collected_ghosts
    
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
    
    def _climb(self, f):
        current_node = self
        while not current_node.is_root:
            f(current_node)
            current_node = current_node.parent

    def __repr__(self):
        properties = ', '.join('{}={}'.format(k, getattr(self, k)) for k in ['property_name', 'property_value', 'children'])
        return '{}({})'.format(type(self).__name__, properties)
