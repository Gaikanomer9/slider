from dataclasses import dataclass, field
from .slo import SLO
from .utils import produce_output
from typing import List, Iterator
import yaml
import os
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

    # TODO: figure out how to make 'rules' display as last item in yaml output
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


def generate_rules(slos: Iterator[SLO], filepath: str, output: str) -> object:
    success_group_rules = []
    info_group_rules = []
    for slo in slos:
        if slo.indicator.ratioMetric is not None:
            g_rt = slo.indicator.ratioMetric.good.metricSource.spec.get("query")
            t_rt = slo.indicator.ratioMetric.total.metricSource.spec.get("query")
            expression = f'sum(rate({g_rt}[{slo.window}])) / sum(rate({t_rt}[{slo.window}]))'
            success_ratio = Rule()
            success_ratio.record = "slo:success:ratio"
            success_ratio.expr = expression
            success_ratio.labels = {
                "id": slo.id,
                "window": slo.window,
                "target": slo.target,
            }
            success_group_rules.append(success_ratio)
        info_target = Rule()
        info_target.record = "slo:info:target"
        info_target.expr = f'vector({slo.target})'
        info_target.labels = {
            "id": slo.id,
            "tenant": slo.tenant,
            "service": slo.service,
            "name": slo.name,
            "window": slo.window,
            "target": slo.target,
            "budgeting_method": "occurrences"
        }
        info_group_rules.append(info_target)
    rule_groups = [
        RuleGroup(name="slider-slo-success-calculations", rules=success_group_rules),
        RuleGroup(name="slider-slo-info-metadata-logging", interval="2m30s", rules=info_group_rules)
    ]
    group = Groups(groups=rule_groups)
    produce_output(output, filepath, group, {"sort_keys": False})
