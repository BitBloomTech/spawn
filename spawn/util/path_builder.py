# spawn
# Copyright (C) 2018-2019, Simmovation Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
"""Path building
"""
import re
import string

LETTERS = string.ascii_lowercase

class PathBuilder:
    """The path builder class

    This class provides a standardised way to build paths and interpolate/format them with values
    """
    def __init__(self, path=''):
        """Initialises :class:`PathBuilder`

        :param path: The initial path. Defaults to an empty string.
        :type path: str
        """
        self._path = path

    def join(self, other):
        """Join two paths by adding ``other`` onto the end of ``self``

        :param other: The path to add to the end of this path
        :type other: str

        :returns: A new path builder with the joined paths
        :rtype: :class:`PathBuilder`
        """
        new_path = '{}/{}'.format(self._path, other) if self._path else other
        return PathBuilder(new_path)

    def join_start(self, other):
        """Join two paths by adding ``other`` onto the start of ``self``

        :param other: The path to add to the start of this path
        :type other: str

        :returns: A new path builder with the joined paths
        :rtype: :class:`PathBuilder`
        """
        new_path = '{}/{}'.format(other, self._path) if self._path else other
        return PathBuilder(new_path)

    def format(self, properties, indices=None):
        """Format the path by interpolating with the properties provided.

        If indices are provided, use them in place of the properties.

        :param properties: The properties to interpolate with.
        :type properties: dict
        :param indices: The indicies to use in place of the properties, if any.
            Defaults to ``None``.
        :type indicies: dict

        :returns: A new instance with the interpolated values
        :rtype: :class:`PathBuilder`
        """
        if indices is not None:
            if properties.keys() != indices.keys():
                raise ValueError('index must be provided for all properties')
        next_path = self._path
        for key in properties.keys():
            token_regex = self._token(key)
            search_result = re.search(token_regex, next_path)
            if search_result:
                index_format = search_result.group('index_format')
                if index_format:
                    if indices is None:
                        raise ValueError('indices must be provided if index formats are defined')
                    substitution = self.index(indices[key], index_format)
                else:
                    substitution = str(properties[key])
                next_path = next_path.replace(search_result.group(0), substitution)
        remaining_values = re.search(self._token('.*'), next_path)
        if remaining_values:
            raise ValueError('No value supplied for token "{}"'.format(remaining_values.group(0)))
        return PathBuilder(next_path)

    @staticmethod
    def _token(value):
        return r'\{' + value + r':?(?P<index_format>[^\}]*)\}'

    def __repr__(self):
        return self._path

    @staticmethod
    def index(index, index_format='1'):
        #pylint: disable=anomalous-backslash-in-string
        """Formats an index given the ``index_format`` provided

        :param index: The index to format
        :type index: int
        :param index_format: The index format (see below for examples).
        :type index_format: str

        :returns: The formatted index
        :rtype: str

        ======= ======================================== =======================
        Format  Description                              Examples
        ======= ======================================== =======================
        0*[\d]+ Padded integer with start value          01 -> 01, 02, 03...
                                                         002 -> 002, 003, 004...
        [a]+    Alphabetical                             a -> a, b, c, d...
                                                         aa -> aa, ab, ac, ad...
        ======= ======================================== =======================
        """
        if re.search(r'0*[\d]+', index_format):
            start_index = int(index_format)
            pad_width = len(index_format)
            return '{index:0>{pad_width}}'.format(index=index + start_index, pad_width=pad_width)
        if re.search(r'[a]+', index_format):
            index_string = ''
            while index > 0:
                next_value, index = index % 26, index // 26
                index_string = LETTERS[next_value] + index_string
            return '{index_string:a>{pad_width}}'.format(
                index_string=index_string, pad_width=len(index_format)
            )

        raise ValueError('index_format has unsupported value {}'.format(index_format))
