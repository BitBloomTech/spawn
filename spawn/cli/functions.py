# spawn
# Copyright (C) 2018, Simmovation Ltd.
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
from spawn.config import (CommandLineConfiguration, CompositeConfiguration,
                          DefaultConfiguration, IniFileConfiguration)
from spawn.parsers import SpecificationFileReader, SpecificationParser
from spawn.plugins import PluginLoader
from spawn.schedulers import LuigiScheduler
from spawn.specification import DictSpecificationConverter
from spawn.util import configure_logging, prettyspec

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
    config = _get_config(**kwargs)
    configure_logging(config.get(APP_NAME, 'log_level'), ctx.invoked_subcommand, config.get(APP_NAME, 'log_console'))
    ctx.obj = kwargs

@cli.command()
@_pass_config
def check_config(config):
    """Check the configuration. Parses the current configuration and prints to stdout
    """
    _print_config(_get_config(**config))

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
    config = _get_config(**{**config, **kwargs})
    specfile = config.get(APP_NAME, 'specfile')
    outfile = config.get(APP_NAME, 'outfile')
    click.echo('Inspecing input file "{}":'.format(click.format_filename(specfile)))
    reader = SpecificationFileReader(specfile)
    parser = SpecificationParser(reader, PluginLoader(config))
    spec = parser.parse()
    spec_dict = DictSpecificationConverter().convert(spec)
    click.echo('Number of leaves: {}'.format(len(spec.root_node.leaves)))
    if outfile is not None:
        format_ = config.get(APP_NAME, 'format')
        with open(outfile, 'w') as f:
            if format_ == 'txt':
                prettyspec(spec_dict, f)
            elif format_ == 'json':
                json.dump(spec_dict, f, indent=2)
        click.echo('Specification details written to {}'.format(f.name))
    else:
        prettyspec(spec_dict)

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
    config = _get_config(**{**config, **kwargs})
    reader = SpecificationFileReader(config.get(APP_NAME, 'specfile'))
    plugin_loader = PluginLoader(config)
    spec = SpecificationParser(reader, plugin_loader).parse()
    plugin_type = config.get(APP_NAME, 'type') or spec.metadata.spec_type
    if not plugin_type:
        raise ValueError((
            'No plugin type defined - please specify the --type argument ' +
            'or add a type property in the spec file'
        ))
    spawner = plugin_loader.create_spawner(plugin_type)
    scheduler = LuigiScheduler(config)
    scheduler.run(spawner, spec)

@cli.command()
@_pass_config
def work(config):
    """Adds a worker to a remote scheduler
    """
    config = _get_config(**{**config, 'local': False})
    scheduler = LuigiScheduler(config)
    scheduler.add_worker()

def _get_config(**kwargs):
    command_line_config = CommandLineConfiguration(**kwargs)
    ini_file_config = IniFileConfiguration(command_line_config.get(APP_NAME, 'config_file'))
    default_config = DefaultConfiguration()
    return CompositeConfiguration(command_line_config, ini_file_config, default_config)

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
