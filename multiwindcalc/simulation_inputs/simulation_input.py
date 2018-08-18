from abc import abstractmethod


class SimulationInput:
    @abstractmethod
    def to_file(self, file_path, editions):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError
