

class TaskSpawner:
    """Base class task spawner"""

    def spawn(self):
        """Create new derivative of luigi.Task for later execution"""
        raise NotImplementedError()

    def branch(self, branch_id=None):
        """Deep copy task input and dependencies so that they can be edited without affecting trunk object"""
        raise NotImplementedError()
