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
"""Utility functions used by consumers of the interface
"""
import functools
import contextlib
import json

from spawn.util import prettyspec

def _stream_wrapper(stream):
    """Wraps a stream so that it is not destroyed when used in a `with` statement
    """
    @contextlib.contextmanager
    def _():
        yield stream
    return _

#pylint: disable=redefined-builtin
def write_inspection(inspection, out, format='json'):
    """Writes the inspection in the format specified

    :param inspection: The result of the spec inspection
    :type inspection: dict
    :param out: The output destination (filename or buffer)
    :type out: str|buffer
    :param output_format: The output format (json|txt)
    :type output_format: str
    """
    buffer = (
        functools.partial(open, out, 'w') if isinstance(out, str) else
        _stream_wrapper(out)
    )
    formatter = (
        functools.partial(prettyspec, inspection) if format == 'txt' else
        functools.partial(json.dump, inspection, indent=2)
    )
    with buffer() as stream:
        formatter(stream)
