from importlib.resources import files
import json
import _jsonnet
from .slo import SLO
from .utils import produce_output

jsonnet_file = "dashboard-template.jsonnet"


def generate_dashboard(slo: SLO, filepath: str, output: str):
    # TODO: template the jsonnet file with slo object
    jsonnet_path = files('slider.data').joinpath(jsonnet_file)
    data = json.loads(_jsonnet.evaluate_file(str(jsonnet_path)))
    produce_output(output, filepath, data)