import click
from pprint import pprint

from .logging import configure_logging
from .prettyspec import prettyspec

from multiwindcalc.parsers import SpecificationFileReader, SpecificationParser
from multiwindcalc.specification import DictSpecificationConverter

@click.group()
@click.option('--log-level', type=click.Choice(['error', 'warning', 'info', 'debug']), default='info')
@click.option('--log-console', is_flag=True)
def cli(log_level, log_console):
    configure_logging(log_level, log_console)

@cli.command()
@click.argument('specfile', type=click.Path(exists=True))
def inspect(specfile):
    click.echo('Inspecing input file "{}":'.format(click.format_filename(specfile)))
    reader = SpecificationFileReader(specfile)
    parser = SpecificationParser(reader)
    spec = parser.parse()
    spec_dict = DictSpecificationConverter().convert(spec)
    prettyspec(spec_dict)
