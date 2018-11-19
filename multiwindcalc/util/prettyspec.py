"""prettyspec spec writer
"""
import sys

from multiwindcalc.util.validation import validate_type

INDENT = '  '

def _prettyspec_impl(spec, indent, outstream):
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