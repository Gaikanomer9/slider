import os
import sys
from glob import glob
import yaml
from yaml import Loader
from slo import Validator
from rules import generate_rules

import click


class SliderGen:
    def __init__(self):
        self.config = {}
        self.verbose = False
        self.validator = Validator()
        self.rules = {}

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            click.echo(f"  config[{key}] = {value}", file=sys.stderr)


pass_slider_gen = click.make_pass_decorator(SliderGen)

@click.group()
@click.option(
    "--config",
    nargs=2,
    multiple=True,
    metavar="KEY VALUE",
    help="Overrides a config key/value pair.",
)
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.version_option("1.0")
@click.pass_context
def cli(ctx, config, verbose):
    """SliderGen is a command line tool that creates
    Prometheus rules on the given OpenSLO specification.
    """
    ctx.obj = SliderGen()
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)



@cli.command()
@click.argument("src", required=True)
@pass_slider_gen
def generate(slider_gen, src):
    """Generates Prometheus rules on the given
    OpenSLO spec files.

    SRC is the directory containing OpenSLO specs.
    """
    files = glob(f"{src}/*")
    if src[-5:] == '.yaml':
        files.append(src)
    for f in files:
        print(f)
        if os.path.isdir(f):
            files.extend(glob(f"{f}/*"))
    for spec in files:
        if spec[-5:] != ".yaml":
            click.echo(f'File {spec} is skipped because only .yaml type is supported')
            continue
        
        with open(spec) as f2:
            sloObj = yaml.load(f2, Loader)

        valid, error = slider_gen.validator.validate_spec(sloObj, "slo-spec.schema.json")
        if not valid:
            click.echo(f'File {spec} is not a valid Open SLO specification: {error}')
            continue
        
        generate_rules(sloObj)

