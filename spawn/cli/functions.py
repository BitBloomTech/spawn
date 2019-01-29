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
"""spawn.cli module
"""
import json
import logging

import click
import luigi.configuration
import luigi.interface

from spawn import __name__ as APP_NAME
from spawn.interface import LocalInterface, spawn_config, write_inspection
from spawn.schedulers import LuigiScheduler
from spawn.util import configure_logging

# Prevent luigi from setting up it's own logging
#pylint: disable=protected-access
luigi.interface.InterfaceLogging._configured = True


LOGGER = logging.getLogger()

#pylint: disable=invalid-name
_pass_config = click.make_pass_decorator(dict)

@click.group()
@click.pass_context
@click.option(
    '--log-level', type=click.Choice(['error', 'warning', 'info', 'debug']),
    default='info', help='The log level'
)
@click.option('--log-console', is_flag=True, help='Write logs to the console')
@click.option(
    '-d', type=click.STRING, multiple=True,
    help='Definitions to override configuration file parameters (e.g. -d spawn.workers=2)'
)
@click.option(
    '--config-file', type=click.Path(exists=None, dir_okay=False, resolve_path=True),
    default=APP_NAME + '.ini', help='Path to the config file.'
)
def cli(ctx, **kwargs):
    """Command Line Interface
    """
    config = spawn_config(**kwargs)
    configure_logging(config.get(APP_NAME, 'log_level'), ctx.invoked_subcommand, config.get(APP_NAME, 'log_console'))
    ctx.obj = kwargs

@cli.command()
@_pass_config
def check_config(config):
    """Check the configuration. Parses the current configuration and prints to stdout
    """
    _print_config(spawn_config(**config))

@cli.command()
@_pass_config
@click.argument('specfile', type=click.Path(exists=True))
@click.option('-o', '--outfile', type=click.Path(), help='write inspection output to file rather than to console')
@click.option(
    '-f', '--format', type=click.Choice(['txt', 'json']),
    default='txt', help='format of specification inspection'
)
def inspect(config, **kwargs):
    """Expand and write to console the contents of the SPECFILE
    """
    config = spawn_config(**{**config, **kwargs})
    specfile = config.get(APP_NAME, 'specfile')
    outfile = config.get(APP_NAME, 'outfile')
    click.echo('Inspecing input file "{}":'.format(click.format_filename(specfile)))
    interface = LocalInterface(config)
    with open(specfile) as fp:
        obj = json.load(fp)
    spec_dict = interface.inspect(obj)
    spec_stats = interface.stats(obj)
    click.echo('Stats: {}'.format('; '.join('{}={}'.format(k, v) for k, v in spec_stats.items())))
    write_inspection(spec_dict, outfile or click.get_text_stream('stdout'), config.get(APP_NAME, 'format'))
    if outfile:
        click.echo('Specification details written to {}'.format(outfile))

@cli.command()
@_pass_config
@click.argument('specfile', type=click.Path(exists=True))
@click.argument('outdir', type=click.Path(file_okay=False, resolve_path=True))
@click.option('--type', type=str, default=None, help='The type of runs to create. Must have a corresponding plugin.')
@click.option(
    '--local/--remote', is_flag=True,
    default=True, help='Run local or remote. Remote running requires a luigi server to be running'
)
def run(config, **kwargs):
    """Runs the SPECFILE contents and write output to OUTDIR
    """
    config = spawn_config(**{**config, **kwargs})
    interface = LocalInterface(config)
    with open(config.get(APP_NAME, 'specfile')) as fp:
        spec_dict = json.load(fp)
    interface.run(spec_dict)

@cli.command()
@_pass_config
def work(config):
    """Adds a worker to a remote scheduler
    """
    config = spawn_config(**{**config, 'local': False})
    scheduler = LuigiScheduler(config)
    scheduler.add_worker()

def _print_config(config, ):
    name_col_width = 0
    names_values = []
    for category in config.categories:
        for key in config.keys(category):
            name = '{}.{}'.format(category, key)
            value = config.get(category, key)
            names_values.append((name, value))
            name_col_width = max(name_col_width, len(name))

    for name, value in names_values:
        click.echo('{name: <{width}}{value}'.format(name=name, value=value, width=name_col_width + 4))
