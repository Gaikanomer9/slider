from decimal import Decimal
import json
import os
from dataclasses import dataclass
import string
from typing import Any, Dict, Union, List

from jsonschema import validate
from jsonschema.validators import RefResolver
from jsonschema import ValidationError, SchemaError

COMMIT_SHA_OPENSLO_SCHEMA = "ca2b59332b6fed9814f1b466877859b4ef68cb2b"

OPENSLO_SCHEMA_FILES = (
    "openslo.schema.json",
    "parts/alertcondition-spec.schema.json",
    "parts/alertnotificationtarget-spec.schema.json",
    "parts/alertpolicy-spec.schema.json",
    "parts/datasource-spec.schema.json",
    "parts/description.schema.json",
    "parts/duration-shorthand.schema.json",
    "parts/general.schema.json",
    "parts/metadata.schema.json",
    "parts/metricsource.schema.json",
    "parts/name.schema.json",
    "parts/service-spec.schema.json",
    "parts/sli-spec.schema.json",
    "parts/slo-spec.schema.json",
    
)


@dataclass
class Metadata:
    name: str
    displayName: str


@dataclass
class MetricSource:
    type: str
    spec: Any


@dataclass
class ThresholdMetric:
    metricSource: MetricSource


@dataclass
class RatioMetric:
    counter: bool
    good: ThresholdMetric
    bad: ThresholdMetric
    total: ThresholdMetric


@dataclass
class Indicator:
    metadata: Metadata
    spec: Union[ThresholdMetric, RatioMetric]


@dataclass
class WindowCalendar:
    startTime: str
    timeZone: str


@dataclass
class TimeWindow:
    duration: str
    isRolling: bool


@dataclass
class Target:
    displayName: str
    op: str
    value: Decimal
    target: Decimal
    timeSliceTarget: Decimal
    timeSliceWindow: str


@dataclass
class SLOSpec:
    description: str
    service: string
    indicator: Indicator
    timeWindow: List[TimeWindow]
    budgetingMethod: str
    objectives: List[Target]


@dataclass
class SLO:
    """
    SLO class represents an internal SLO object which takes only part
    of data from OpenSLO specification. It supports loading, validation
    and generation of the Prometheus rules.
    """
    apiVersion: str
    kind: str
    metadata: Metadata
    spec: SLOSpec


def build_slo_from_yaml(parsed_yaml: Dict[Any, Any]) -> SLO:
    return SLO(**parsed_yaml)





"""
**************************
Code below is expiremental
**************************
"""


def validateSpecFromLocal(schema_search_abs_path, json_data, schema_id):
    """
    load the json file and validate against loaded schema
    """
    try:
        schemastore = loadSchemaFromFiles(schema_search_abs_path)
        schema = schemastore.get("https://openslo.com/schemas/v1/parts/%s" %
                                 schema_id)

        resolver = RefResolver("file:/%s" %
                               os.path.join(schema_search_abs_path, schema_id),
                               schema, schemastore)
        validate(json_data, schema, resolver=resolver)
        return True
    except ValidationError as error:
        print(error)
        # handle validation error 
        pass
    except SchemaError as error:
        print(error)
        # handle schema error
        pass
    return False


def loadSchemaFromFiles(schema_search_abs_path: str) -> dict:
    schemastore = {}
    schema = None
    fnames = os.listdir(schema_search_abs_path)
    fnames = [os.path.join(schema_search_abs_path, p) for p in fnames]
    for fname in fnames:
        fpath = os.path.join(schema_search_abs_path, fname)
        if os.path.isdir(fpath):
            sub_fnames = os.listdir(fpath)
            sub_fnames = [os.path.join(fpath, p) for p in sub_fnames]
            fnames.extend(sub_fnames)
        if fpath[-5:] == ".json":
            with open(fpath, "r") as schema_fd:
                schema = json.load(schema_fd)
                if "$id" in schema:
                    schemastore[schema["$id"]] = schema
    return schemastore


# vld = Validator()
# with open("examples/slo-getting-started.yaml") as f2:
#     testSLO = yaml.load(f2, Loader)

# sloObject = dict_to_slo(testSLO)


# if vld.validate_spec(testSLO, "slo-spec.schema.json"):
#     print("Schema was valid")
# with open("examples/slo-getting-started.yaml") as f2:
#     testSLO = yaml.load(f2, Loader)
# if validateSpecFromLocal(os.getcwd()+"/OpenSLO", testSLO
# # "slo-spec.schema.json"):
#     print("Schema was valid")
