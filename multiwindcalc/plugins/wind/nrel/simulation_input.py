"""Contains definitions for NREL :class:`SimulationInput`
"""
from os import path
import csv
from multiwindcalc.simulation_inputs import SimulationInput


def _absolutise_path(line, root_dir, local_path):
    local_path = local_path.strip('"')
    return line.replace(local_path, str(path.join(root_dir, local_path)))


class NRELSimulationInput(SimulationInput):
    """
    Handles contents of input files for NREL's aeroelastic modules such as FAST, AeroDyn and TurbSim.
    These tend to be of a whitespace separated {value|key} format with newlines separating key:value pairs
    """
    def __init__(self, input_lines, root_folder):
        """Initialises :class:`NRELSimulationInput`

        :param input_lines: The lines of the input file
        :type input_lines: list
        :param root_folder: The root folder containing the input file
        :type root_folder: path-like
        """
        self._input_lines = input_lines
        self._absolutise_paths(root_folder, self._lines_with_paths())

    @classmethod
    def from_file(cls, file_path):
        """Creates a :class:`NRELSimulationInput` by loading a file

        :param file_path: The file path to load
        :type file_path: path-like

        :returns: The simulation input object
        :rtype: An instance of :class:`NRELSimulationInput`
        """
        with open(file_path, 'r') as fp:
            input_lines = fp.readlines()
        root_folder = path.abspath(path.split(file_path)[0])
        return cls(input_lines, root_folder)

    def to_file(self, file_path):
        """Writes the contents of the input file to disk

        :param file_path: The path of the file to write
        :type file_path: path-like
        """
        with open(file_path, 'w') as fw:
            for line in self._input_lines:
                fw.write(line)

    def __setitem__(self, key, value):
        i, parts = self._get_index_and_parts(key)
        self._input_lines[i] = self._input_lines[i].replace(parts[0], str(value).strip('"'))

    def __getitem__(self, key):
        value = self._get_index_and_parts(key)[1][0]
        return value.strip('"')

    @staticmethod
    def _get_parts(line):
        # CSV reader is the easiest way to interpret quoted strings encompassing spaces as one part
        return next(csv.reader([line], delimiter=' ', quotechar='"', skipinitialspace=True))

    def _get_index_and_parts(self, key):
        for i, line in enumerate(self._input_lines):
            parts = self._get_parts(line)
            if len(parts) > 1 and parts[1] == key:
                return i, parts
        raise KeyError('parameter \'{}\' not found'.format(key))

    def _absolutise_paths(self, root_folder, lines):
        for i in lines:
            parts = self._get_parts(self._input_lines[i])
            rel_path = parts[0].strip('"')
            self._input_lines[i] = self._input_lines[i].replace(rel_path,
                                                                path.abspath(path.join(root_folder, rel_path)))

    def _lines_with_paths(self):
        return []


class TurbsimInput(NRELSimulationInput):
    """Handles contents of TurbSim (FAST wind generation) input file"""
    pass


class AerodynInput(NRELSimulationInput):
    """Handles contents of Aerodyn (FAST aerodynamics) input file"""
    def _lines_with_paths(self):
        num_foils = int(self['NumFoil'])
        index, _ = self._get_index_and_parts('FoilNm')
        return range(index, index + num_foils)


class FastInput(NRELSimulationInput):
    """Handles contents of primary FAST input file"""
    def _lines_with_paths(self):
        def is_file_path(key):
            return key in ['TwrFile', 'ADFile', 'ADAMSFile'] or 'BldFile' in key
        lines = []
        for i in range(len(self._input_lines)):
            parts = self._get_parts(self._input_lines[i])
            if len(parts) > 1 and is_file_path(parts[1]):
                lines.append(i)
        return lines