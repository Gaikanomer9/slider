import os
import sys
from glob import glob
import yaml
from yaml import Loader
from slo import build_slo_from_yaml
from validator import Validator
from rules import generate_rules
from dashboard import generate_dashboard

import click


class Slider:
    def __init__(self):
        self.config = {}
        self.verbose = False
        self.validator = Validator()
        self.slos = {}

    def set_config(self, key, value):
        self.config[key] = value
        if self.verbose:
            click.echo(f"  config[{key}] = {value}", file=sys.stderr)

    def validate_all(self):
        for slo in self.slos.values():
            self.validator.validate_slo(slo)

    def generate_all(self):
        generate_rules(self.slos.values())
    
    def gen_dashboard(self):
        if "dashpath" not in self.config:
            raise Exception("please specify the path to save the dashboard slider --config dashpath ../playground/grafana/provisioning/dashboards/table.json ")
        generate_dashboard(self.slos, self.config.get("dashpath"))

    def read_yaml_files(self, src):
        files = glob(f"{src}/*")
        if src[-5:] == '.yaml':
            files.append(src)
        for f in files:
            if os.path.isdir(f):
                files.extend(glob(f"{f}/*"))
        for spec in files:
            if spec[-5:] != ".yaml":
                click.echo((f'File {spec} is skipped'
                            'because only .yaml type is supported'))
                continue
            with open(spec) as f2:
                docs = yaml.load_all(f2, Loader)
                for doc in docs:
                    slo_parsed = build_slo_from_yaml(doc)
                    slo_name = slo_parsed.metadata.name
                    if slo_name in self.slos:
                        raise ValueError(
                            f'Found a duplicate SLO name {slo_name}, aborting')
                    self.slos[slo_name] = slo_parsed


pass_slider = click.make_pass_decorator(Slider)


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


@click.command(cls=AliasedGroup)
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
    """Slider is a command line tool that creates
    Prometheus rules on the given OpenSLO specification.
    """
    ctx.obj = Slider()
    ctx.obj.verbose = verbose
    for key, value in config:
        ctx.obj.set_config(key, value)


@cli.command()
@click.argument("src", required=True)
@pass_slider
def verify(slider, src):
    """Verify the source OpenSLO specifications
    """
    slider.read_yaml_files(src)
    slider.validate_all()
    click.echo("SLO specs are valid")


@cli.command()
@click.argument("src", required=True)
# https://github.com/pallets/click/issues/2351
@click.option("-a", "--all", "gen_all", flag_value=1, default=True,
                help="Generate both prom rules and dashboard config [default]")
@click.option("-r", "--rules", "gen_all", flag_value=0,
                help="Only generate recording and alerting rules, no dashboard")
@pass_slider
def generate(slider, src, gen_all):
    """Generates Prometheus rules on the given
    OpenSLO spec files.

    SRC is a yaml file with an OpenSLO spec or a directory of such files.
    """
    # Load all files and perform validation against OpenSLO schema
    slider.read_yaml_files(src)
    slider.validate_all()
    slider.generate_all()
    if gen_all:
        slider.gen_dashboard()
