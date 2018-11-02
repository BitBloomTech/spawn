import click
from pprint import pprint
from os import path
from luigi import build, server
import luigi.interface
import luigi.configuration

# Prevent luigi from setting up it's own logging
luigi.interface.setup_interface_logging.has_run = True

from .logging import configure_logging
from .prettyspec import prettyspec

from multiwindcalc.parsers import SpecificationFileReader, SpecificationParser, SpecificationNodeParser
from multiwindcalc.specification import DictSpecificationConverter
from multiwindcalc.spawners import TurbsimSpawner, FastSimulationSpawner
from multiwindcalc.simulation_inputs import TurbsimInput, FastInput
from multiwindcalc.schedulers import LuigiScheduler

DEFAULT_PORT = 8082

import logging
LOGGER = logging.getLogger()

@click.group()
@click.pass_context
@click.option('--log-level', type=click.Choice(['error', 'warning', 'info', 'debug']), default='info', help='The log level')
@click.option('--log-console', is_flag=True, help='Write logs to the console')
def cli(ctx, log_level, log_console):
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
@click.option('--local/--remote', is_flag=True, default=True, help='Run local or remote. Remote running requires a luigi server to be running')
@click.option('--workers', type=click.IntRange(1, 100), default=4, help='The number of workers')
@click.option('--port', type=click.IntRange(1000, 9999), default=DEFAULT_PORT, help='The port on which the remote scheduler is running')
def run(specfile, outdir, local, workers, port):
    """Runs the SPECFILE contents and write output to OUTDIR
    """
    spawner = create_spawner()
    reader = SpecificationFileReader(specfile)
    parser = SpecificationParser(reader)
    spec = parser.parse()
    scheduler = LuigiScheduler(
        outdir=outdir,
        local=local,
        workers=workers,
        port=port,
        runner_type='process',
        turbsim_exe_path=EXE_PATHS['turbsim'],
        fast_exe_path=EXE_PATHS['fast']
    )
    scheduler.run(spawner, spec)

@cli.command()
@click.argument('port', type=click.IntRange(1000, 9999), default=DEFAULT_PORT)
def serve(port):
    """Runs the luigi server, for running using the centralised scheduler and viewing the UI
    """
    server.run(api_port=port)

example_data_folder = path.realpath('example_data')

EXE_PATHS = {
    'turbsim': path.join(example_data_folder, 'TurbSim.exe'),
    'fast': path.join(example_data_folder, 'FASTv7.0.2.exe')
}

def create_spawner():
    wind_spawner = TurbsimSpawner(TurbsimInput.from_file(path.join(example_data_folder, 'fast_input_files',
                                                                   'TurbSim.inp')))
    return FastSimulationSpawner(FastInput.from_file(path.join(example_data_folder, 'fast_input_files',
                                                               'NRELOffshrBsline5MW_Onshore.fst')),
                                 wind_spawner)