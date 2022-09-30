from importlib.resources import files
import json
import _jsonnet
from .slo import SLO

jsonnet_file = "dashboard-template.jsonnet"


def generate_dashboard(slo: SLO, filepath: str):
    # TODO: template the jsonnet file with slo object
    jsonnet_path = files('slider.data').joinpath(jsonnet_file)
    data = json.loads(_jsonnet.evaluate_file(str(jsonnet_path)))
    with open(filepath, 'w') as f:
        json.dump(data, f)
