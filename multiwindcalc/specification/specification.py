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
    def __init__(self, parent, property_name, property_value):
        self._parent = parent
        self._property_name = property_name
        self._property_value = property_value
        self._children = []
        if self._parent is not None:
            self._parent.add_child(self)
    
    @classmethod
    def create_root(cls):
        return SpecificationNode(None, None, None)
    
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
        if not self.children:
            return [self]
        leaves = []
        for c in self.children:
            leaves += c.leaves
        return leaves

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
    def collected_properties(self):
        properties = {}
        current_node = self
        while not current_node.is_root:
            # Only update the property if it is not already set
            # Child nodes should override parent nodes
            properties.setdefault(current_node.property_name, current_node.property_value)
            current_node = current_node.parent
        return properties