from abc import abstractmethod


class SimulationInput:
    """Handler of inputs for a simulation that will typically be parsed from and written to a file"""

    @classmethod
    def from_file(cls, file_path):
        raise NotImplementedError()

    @abstractmethod
    def to_file(self, file_path):
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()
