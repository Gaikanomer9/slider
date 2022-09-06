import json
import _jsonnet
from slo import SLO

jsonnet_file = "dashboards/jsonnet/template.jsonnet"


def generate_dashboard(slo: SLO, filepath: str):
    # TODO: template the jsonnet file with slo object
    data = json.loads(_jsonnet.evaluate_file(jsonnet_file))
    with open(filepath, 'w') as f:
        json.dump(data, f)
