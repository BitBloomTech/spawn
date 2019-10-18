import json
import copy

from .simulation_input import SimulationInput


class JsonSimulationInput(SimulationInput):
    """A dictionary input written as a JSON file"""

    def __init__(self, parameter_set, **write_options):
        """Create a instance of :class:`JsonSimulationInput`

        :param parameter_set: Baseline parameter set
        :type parameter_set: dict
        """
        self._parameter_set = copy.deepcopy(parameter_set)
        self._write_options = write_options

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as fp:
            return cls(json.load(fp))

    def to_file(self, file_path):
        with open(file_path, 'w') as fw:
            json.dump(self._parameter_set, fw, **self._write_options)

    def hash(self):
        return hash(json.dumps(self._parameter_set))

    def __setitem__(self, key, value):
        self._parameter_set.__setitem__(key, value)

    def __getitem__(self, item):
        return self._parameter_set.__getitem__(item)
