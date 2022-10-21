from importlib.resources import files
import json
import _jsonnet
from .slo import SLO
from .utils import produce_output
from .rules import Groups
from typing import Iterator

jsonnet_file = "dashboard-template.jsonnet"


def generate_dashboard(slos: Iterator[SLO], filepath: str, output: str, groups: Groups):
    for slo in slos:
        jsonnet_path = files('slider').joinpath("data").joinpath(jsonnet_file) 
        total_query = slo.indicator.ratioMetric.total.metricSource.spec["query"]
        good_query = slo.indicator.ratioMetric.good.metricSource.spec["query"]
        window = slo.spec.timeWindow[0].duration
        data = json.loads(_jsonnet.evaluate_file(str(jsonnet_path),
                        ext_vars={'SLO_INFO_TARGET': 'slo:info:target',
                                  'SLO_SUCCESS_RATIO': 'slo:success:ratio',
                                  'SLO_TOTAL_QUERY': total_query,
                                  'SLO_GOOD_QUERY': good_query,
                                  'SLO_WINDOW': window,
                                  }))
        produce_output(output, filepath, data, format="json")