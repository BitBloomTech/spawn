"""Defines the base class for the spawn interface
"""
from abc import ABC, abstractmethod

class SpawnInterface(ABC):
    """Defines the abstract base class :class:`SpawnInterface`

    Sub-classes should provide implementations for `inspect` and `run`
    """
    @abstractmethod
    def inspect(self, spec_dict):
        """Inspect the object

        :param spec_dict: The specfile object
        :type spec_dict: dict

        :returns: An expanded inspection dict
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    def stats(self, spec_dict):
        """Calculate stats for the spec

        :param spec_dict: The specfile object
        :type spec_dict: dict

        :returns: An dict containing stats about the object
        :rtype: dict
        """
        raise NotImplementedError()

    @abstractmethod
    def run(self, spec_dict):
        """Run the object

        :param spec_dict: The specfile object
        :type spec_dict: dict
        """
        raise NotImplementedError()
