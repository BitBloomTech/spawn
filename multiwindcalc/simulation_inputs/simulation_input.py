"""Abstract base class for simulation inputs
"""
from abc import abstractmethod


class SimulationInput:
    """Handler of inputs for a simulation that will typically be parsed from and written to a file"""

    @classmethod
    def from_file(cls, file_path):
        """Creates a :class:`SimulationInput` by loading a file

        :param file_path: The file path to load
        :type file_path: path-like

        :returns: The simulation input object
        :rtype: An instance of :class:`SimulationInput`
        """
        raise NotImplementedError()

    @abstractmethod
    def to_file(self, file_path):
        """Writes the contents of the input file to disk

        :param file_path: The path of the file to write
        :type file_path: path-like
        """
        raise NotImplementedError()
    
    @abstractmethod
    def hash(self):
        """Returns a hash of the contents of the file

        :returns: The hash
        :rtype: str
        """
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError()
