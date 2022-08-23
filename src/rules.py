from dataclasses import dataclass, field
from slo import SLO
from typing import List
import yaml
import click

yaml.emitter.Emitter.prepare_tag = lambda self, tag: ''


@dataclass
class Rule(yaml.YAMLObject):
    yaml_tag = u'!Rule'

    record: str = field(default_factory=lambda: None)
    expr: str = field(default_factory=lambda: None)
    alert: str = field(default_factory=lambda: None)
    For: str = field(default_factory=lambda: None)
    labels: dict = field(default_factory=lambda: {})
    annotations: dict = field(default_factory=lambda: {})


@dataclass
class RuleGroup:
    yaml_tag = u'!RuleGroup'

    name: str
    rules: List[Rule]
    interval: str = field(default_factory=lambda: None)
    partial_response_strategy: str = field(default_factory=lambda: None)


@dataclass
class Groups:
    yaml_tag = u'!Groups'

    groups: List[RuleGroup]


def prom_representer(dumper: yaml.Dumper,
                     obj) -> yaml.nodes.MappingNode:
    dumpRule = {k: val for (k, val) in obj.__dict__.items()
                if val is not None and val != {}}
    return dumper.represent_mapping(obj.yaml_tag, dumpRule)


yaml.add_representer(Rule, prom_representer)
yaml.add_representer(RuleGroup, prom_representer)
yaml.add_representer(Groups, prom_representer)


def generate_rules(slo: SLO) -> object:

    indicator = slo.spec.indicator
    time_window = slo.spec.timeWindow
    expression = ""
    rules = []
    if indicator.ratioMetric is not None:
        g_rt = indicator.ratioMetric.good.metricSource.spec.get("query")
        t_rt = indicator.ratioMetric.total.metricSource.spec.get("query")
        w = time_window[0].duration
        expression = f'sum(rate({g_rt}[{w}])) / sum(rate({t_rt}[{w}]))'
        rule = Rule()
        rule.record = "slo:success:ratio"
        rule.expr = expression
        rule.labels = {
            "id": slo.metadata.name,
            "name": slo.metadata.name,
            "window": w,
            "target": slo.spec.objectives[0].targetPercent / 100,
            "budgeting_method": "occurrences"
        }
        rules.append(rule)
    rule_groups = [RuleGroup(name="slider1", rules=rules)]
    group = Groups(groups=rule_groups)
    click.echo(yaml.dump(group, sort_keys=False))
