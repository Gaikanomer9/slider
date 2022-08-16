from decimal import Decimal
from dataclasses import dataclass, field
import string
from typing import Any, Dict, Union, List

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
    annotations: dict = field(default_factory=lambda: {})


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

    def __post_init__(self):
        self.metadata = Metadata(**self.metadata)
        self.spec = SLOSpec(**self.spec)


def build_slo_from_yaml(parsed_yaml: Dict[Any, Any]) -> SLO:
    return SLO(**parsed_yaml)
