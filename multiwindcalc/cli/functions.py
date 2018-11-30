"""multiwindcalc.cli module
"""
import configparser
import click
from pprint import pprint
from os import path
from luigi import build, server
import luigi.interface
import luigi.configuration

# Prevent luigi from setting up it's own logging
luigi.interface.setup_interface_logging.has_run = True

from multiwindcalc import __name__ as APP_NAME
from multiwindcalc.util import configure_logging, prettyspec
from multiwindcalc.parsers import SpecificationFileReader, SpecificationParser, SpecificationNodeParser
from multiwindcalc.specification import DictSpecificationConverter
from multiwindcalc.plugins.wind.nrel import TurbsimSpawner, FastSimulationSpawner, TurbsimInput, FastInput
from multiwindcalc.schedulers import LuigiScheduler
from multiwindcalc.config import CommandLineConfiguration, IniFileConfiguration, DefaultConfiguration, CompositeConfiguration
from multiwindcalc.plugins import PluginLoader

import logging
LOGGER = logging.getLogger()

@click.group()
@click.pass_context
@click.option('--log-level', type=click.Choice(['error', 'warning', 'info', 'debug']), default='info', help='The log level')
@click.option('--log-console', is_flag=True, help='Write logs to the console')
def cli(ctx, log_level, log_console):
    """Command Line Interface
    """
    configure_logging(log_level, ctx.invoked_subcommand, log_console)

@cli.command()
@click.argument('specfile', type=click.Path(exists=True))
def inspect(specfile):
    """Expand and write to console the contents of the SPECFILE
    """
    click.echo('Inspecing input file "{}":'.format(click.format_filename(specfile)))
    reader = SpecificationFileReader(specfile)
    parser = SpecificationParser(reader)
    spec = parser.parse()
    spec_dict = DictSpecificationConverter().convert(spec)
    prettyspec(spec_dict)

@cli.command()
@click.argument('specfile', type=click.Path(exists=True))
@click.argument('outdir', type=click.Path(file_okay=False, resolve_path=True))
@click.option('--type', type=str, default=None, help='The type of runs to create. Must have a corresponding plugin.')
@click.option('--local/--remote', is_flag=True, default=True, help='Run local or remote. Remote running requires a luigi server to be running')
@click.option('-d', type=click.STRING, multiple=True, help='Definitions to override configuration file parameters (e.g. -d multiwindcalc.workers=2)')
@click.option('--config-file', type=click.Path(exists=None, dir_okay=False, resolve_path=True), default=APP_NAME + '.ini', help='Path to the config file.')
def run(**kwargs):
    """Runs the SPECFILE contents and write output to OUTDIR
    """
    config = _get_config(**kwargs)
    spec = SpecificationParser(SpecificationFileReader(config.get(APP_NAME, 'specfile'))).parse()
    plugin_type = config.get(APP_NAME, 'type') or spec.metadata.type
    if not plugin_type:
        raise ValueError('No plugin type defined - please specify the --type argument or add a type property in the spec file')
    plugin_loader = PluginLoader(config)
    spawner = plugin_loader.create_spawner(plugin_type)
    scheduler = LuigiScheduler(config)
    scheduler.run(spawner, spec)

@cli.command()
@click.option('-d', type=click.STRING, multiple=True, help='Definitions to override configuration file parameters (e.g. -d multiwindcalc.workers=2)')
@click.option('--config-file', type=click.Path(exists=None, dir_okay=False, resolve_path=True), default=APP_NAME + '.ini', help='Path to the config file.')
def serve(**kwargs):
    """Runs the luigi server, for running using the centralised scheduler and viewing the UI
    """
    config = _get_config(**kwargs)
    server.run(api_port=config.get('server', 'port'))

def _get_config(**kwargs):
    command_line_config = CommandLineConfiguration(**kwargs)
    ini_file_config = IniFileConfiguration(command_line_config.get(APP_NAME, 'config_file'))
    default_config = DefaultConfiguration()
    return CompositeConfiguration(command_line_config, ini_file_config, default_config)