import os

import shutil

from sphinx.cmd.build import build_main as build

GENERATED_RSTS = [
    'multiwindcalc',
    'multiwindcalc.cli',
    'multiwindcalc.parsers',
    'multiwindcalc.runners',
    'multiwindcalc.schedulers',
    'multiwindcalc.simulation_inputs',
    'multiwindcalc.spawners',
    'multiwindcalc.specification',
    'multiwindcalc.tasks',
    'multiwindcalc.util'
]

def rst_contents(module):
    underline = '='*len(module)
    return f'{module}\n{underline}\n\n.. automodule:: {module}\n\t:members:\n\t:imported-members:\n'

def generate():
    docs_dir = os.path.join(os.getcwd(), 'docs')
    build_dir = os.path.join(docs_dir, '_build')
    api_docs_dir = os.path.join(docs_dir, 'api')
    if os.path.isdir(api_docs_dir):
        shutil.rmtree(api_docs_dir)
    os.mkdir(api_docs_dir)
    for file in GENERATED_RSTS:
        with open(os.path.join(api_docs_dir, file + '.rst'), 'w+') as fp:
            fp.write(rst_contents(file))
    build([docs_dir, build_dir])

if __name__ == '__main__':
    generate()