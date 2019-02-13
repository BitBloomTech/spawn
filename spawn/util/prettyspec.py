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
"""prettyspec spec writer
"""
import sys

from spawn.util.validation import validate_type

INDENT = '  '

def _prettyspec_impl(spec, indent, outstream):
    # pylint: disable=too-many-branches
    if spec.get('base_file'):
        outstream.write('base_file: {}\n'.format(spec['base_file']))
    if 'metadata' in spec:
        metadata = spec['metadata']
        if metadata.get('creation_time'):
            outstream.write('creation_time: {}'.format(metadata['creation_time']))
        if metadata.get('notes'):
            outstream.write('notes: {}'.format(metadata['notes']))
    if 'spec' in spec:
        for node in spec['spec']:
            _prettyspec_impl(node, indent, outstream)
    if 'name' in spec and 'value' in spec:
        if 'index' in spec:
            name = '{}[{}]'.format(spec['name'], spec['index'])
        else:
            name = spec['name']
        outstream.write('{}{}: {}'.format(INDENT * indent, name, spec['value']))
    if spec.get('ghosts'):
        outstream.write(' | {}'.format(', '.join('_{}: {}'.format(k, v) for k, v in spec['ghosts'].items())))
    if spec.get('path'):
        outstream.write(' | path: {}'.format(spec['path']))
    outstream.write('\n')
    if 'children' in spec:
        for child in spec.get('children'):
            _prettyspec_impl(child, indent + 1, outstream)

def prettyspec(spec, outstream=None):
    """Writes the given spec tree to the stream provided
    """
    validate_type(spec, dict, 'spec')
    _prettyspec_impl(spec, 0, outstream or sys.stdout)
