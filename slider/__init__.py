import os
import sys
from glob import glob
import yaml
from yaml import Loader
from .slo import build_slo_from_yaml
from .validator import Validator
from .rules import generate_rules
from .dashboard import generate_dashboard

import click

# TODO: there shouldn't be this much stuff in __init__.py

class Slider:
    def __init__(self):
        self.config = {}
        self.verbose = False
        self.validator = Validator()
        self.slos = {}
        self.tenant = ""
        self.output = ""

    def validate_all(self):
        for slo in self.slos.values():
            self.validator.validate_slo(slo)

    def gen_rules(self, rulefile="rules.yaml"):
        generate_rules(self.slos.values(), rulefile, self.output)
    
    def gen_dashboards(self, dashfile="dashboard.json"):
        # TODO: generate a separate dashboard file per SLO
        #       maybe use "dashboard-{{slo.id}}.json" as file template
        #       assuming colons in filenames isn't an issue on popular filesystems
        generate_dashboard(self.slos, dashfile, self.output)

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
                    slo_parsed.set_tenant(self.tenant)
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
@click.option("--verbose", "-v", is_flag=True, help="Enables verbose mode.")
@click.version_option("1.0")
@click.pass_context
def cli(ctx, verbose):
    """Slider is a command line tool that creates
    Prometheus rules on the given OpenSLO specification.
    """
    ctx.obj = Slider()
    ctx.obj.verbose = verbose


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
@click.option("--tenant", type=str,
                help="Define a tenant for the SLOs being processed")
# https://github.com/pallets/click/issues/2351
@click.option("-a", "--all", "gen_all", flag_value=1, default=True,
                help="Generate both prom rules and dashboard config [default]")
@click.option("-r", "--rules", "gen_all", flag_value=0,
                help="Only generate recording and alerting rules, no dashboard")
@click.option("-o", "--output", "output", type=str, default=".",
                help="Output directory for Prometheus rules and dashboards")
@pass_slider
def generate(slider, src, tenant, gen_all, output):
    """Generates Prometheus rules on the given
    OpenSLO spec files.

    SRC is a yaml file with an OpenSLO spec or a directory of such files.
    """
    if tenant:
        slider.tenant = tenant
    if output:
        slider.output = output
    # Load all files and perform validation against OpenSLO schema
    slider.read_yaml_files(src)
    slider.validate_all()
    slider.gen_rules()
    if gen_all:
        slider.gen_dashboards()
