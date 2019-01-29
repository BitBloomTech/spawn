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
