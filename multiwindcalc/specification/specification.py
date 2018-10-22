from multiwindcalc.util import PathBuilder

class SpecificationModel:
    def __init__(self, base_file, root_node, metadata):
        self._base_file = base_file
        self._root_node = root_node
        self._metadata = metadata

    @property
    def base_file(self):
        return self._base_file
    
    @property
    def root_node(self):
        return self._root_node
    
    @property
    def metadata(self):
        return self._metadata

class SpecificationMetadata:
    def __init__(self, creation_time, notes):
        self._creation_time = creation_time
        self._notes = notes
    
    @property
    def creation_time(self):
        return self._creation_time
    
    @property
    def notes(self):
        return self._notes

class SpecificationNode:
    def __init__(self, parent, property_name, property_value, path):
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
        return SpecificationNode(None, None, None, path)
    
    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children
    
    def add_child(self, child):
        if child not in self._children:
            self._children.append(child)
    
    @property
    def leaves(self):
        if self._leaves is None:
            self._leaves = sum([c.leaves for c in self.children], []) if self.children else [self]
        return self._leaves
    
    @property
    def root(self):
        if self._root is None:
            current_node = self
            while not current_node.is_root:
                current_node = current_node.parent
            self._root = current_node
        return self._root

    @property
    def is_root(self):
        return self._parent is None
    
    @property
    def property_name(self):
        return self._property_name
    
    @property
    def property_value(self):
        return self._property_value
    
    @property
    def index(self):
        if self.parent is not None:
            return self.parent.children.index(self)
        return -1
    
    @property
    def collected_properties(self):
        if self._collected_properties is None:
            properties = {}
            def _f(node):
                properties.setdefault(node.property_name, node.property_value)
            self._climb(_f)
            self._collected_properties = properties
        return self._collected_properties
    
    @property
    def collected_indices(self):
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