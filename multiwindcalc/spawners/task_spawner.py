

class TaskSpawner:
    """Base class task spawner"""

    def spawn(self, path, metadata):
        """Create new derivative of luigi.Task for later execution"""
        raise NotImplementedError()

    def branch(self):
        """Deep copy task input and dependencies so that they can be edited without affecting trunk object"""
        raise NotImplementedError()
