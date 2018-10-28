

class TaskSpawner:
    """Base class task spawner"""
    def __init__(self):
        self._metadata = {}

    def spawn(self, path, metadata):
        """Create new derivative of luigi.Task for later execution"""
        raise NotImplementedError()

    def branch(self):
        """Deep copy task input and dependencies so that they can be edited without affecting trunk object"""
        raise NotImplementedError()

    def update_meta_property(self, key, value):
        self._metadata[key] = value
