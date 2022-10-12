from decimal import Decimal
from dataclasses import dataclass, field
from typing import Any, Dict, List

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
    # TODO: enforce rules: few characters allowed in names (definitively no spaces)
    name: str = field(default_factory=lambda: "")
    displayName: str = field(default_factory=lambda: "")
    annotations: dict = field(default_factory=lambda: {})


@dataclass
class MetricSource:
    type: str = field(default_factory=lambda: None)
    spec: Any = field(default_factory=lambda: None)


@dataclass
class ThresholdMetric:
    metricSource: MetricSource = field(default_factory=lambda: None)

    def __post_init__(self):
        if self.metricSource is not None:
            self.metricSource = MetricSource(**self.metricSource)


@dataclass
class RatioMetric:
    counter: bool = field(default_factory=lambda: None)
    good: ThresholdMetric = field(default_factory=lambda: None)
    bad: ThresholdMetric = field(default_factory=lambda: None)
    total: ThresholdMetric = field(default_factory=lambda: None)

    def __post_init__(self):
        if self.good is not None:
            self.good = ThresholdMetric(**self.good)
        if self.bad is not None:
            self.bad = ThresholdMetric(**self.bad)
        if self.total is not None:
            self.total = ThresholdMetric(**self.total)


@dataclass
class Indicator:
    metadata: Metadata = field(default_factory=lambda: None)
    thresholdMetric: ThresholdMetric = field(
        default_factory=lambda: None)
    ratioMetric: RatioMetric = field(default_factory=lambda: None)

    def __post_init__(self):
        if self.metadata is not None:
            self.metadata = Metadata(**self.metadata)
        if self.thresholdMetric is not None:
            self.thresholdMetric = ThresholdMetric(**self.thresholdMetric)
        if self.ratioMetric is not None:
            self.ratioMetric = RatioMetric(**self.ratioMetric)


@dataclass
class TimeWindow:
    duration: str


@dataclass
class Target:
    displayName: str = field(default_factory=lambda: None)
    op: str = field(default_factory=lambda: None)
    value: Decimal = field(default_factory=lambda: None)
    target: Decimal = field(default_factory=lambda: None)
    targetPercent: Decimal = field(default_factory=lambda: None)
    timeSliceTarget: Decimal = field(default_factory=lambda: None)
    timeSliceWindow: str = field(default_factory=lambda: None)


@dataclass
class SLOSpec:
    indicator: Indicator
    timeWindow: List[TimeWindow]
    objectives: List[Target]
    description: str = field(default_factory=lambda: "")
    # TODO: enforce rules: few characters allowed in services (definitively no spaces)
    service: str = field(default_factory=lambda: "")
    budgetingMethod: str = field(default_factory=lambda: "")

    def __post_init__(self):
        self.indicator = Indicator(**self.indicator)
        time_windows = []
        for window in self.timeWindow:
            time_windows.append(TimeWindow(**window))
        self.timeWindow = time_windows
        objs = []
        for objective in self.objectives:
            objs.append(Target(**objective))
        self.objectives = objs


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

        # Let's make the object easier to use
        self.tenant = ""
        self.service = self.spec.service
        self.name = self.metadata.name
        self.gen_id()
        self.indicator = self.spec.indicator
        self.window = self.spec.timeWindow[0].duration # Implied rolling window; calendar-aligned not supported
        if self.spec.objectives[0].targetPercent:
            self.targetPercent = self.spec.objectives[0].targetPercent
            self.target = self.targetPercent / 100
        elif self.spec.objectives[0].target:
            self.target = self.spec.objectives[0].target
            self.targetPercent = self.target * 100

    def gen_id(self):
        self.id = f"{self.tenant}:{self.service}:{self.name}"

    def set_tenant(self, tenant: str):
        self.tenant = tenant
        self.gen_id()


def build_slo_from_yaml(parsed_yaml: Dict[Any, Any]) -> SLO:
    return SLO(**parsed_yaml)
