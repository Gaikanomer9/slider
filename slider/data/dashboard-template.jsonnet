local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local singlestat = grafana.singlestat;
local graphPanel = grafana.graphPanel;
local prometheus = grafana.prometheus;

local sloTarget =
  singlestat.new(
    title='SLO Target',
    datasource='Prometheus',
    format='none',
    valueName='name',
  ).addTarget(
    prometheus.target(
      std.extVar("SLO_INFO_TARGET") + '{id="$service_id"}',
      legendFormat='{{ target }}',
    )
  );

local sloWindow =
  singlestat.new(
    title='SLO Window',
    datasource='Prometheus',
    format='none',
    valueName='name',
  ).addTarget(
    prometheus.target(
      std.extVar("SLO_INFO_TARGET") + '{id="$service_id"}',
      legendFormat='{{ window }}',
    )
  );

local sloSuccessRatioGraph =
  graphPanel.new(
    title='SLO Performance',
    datasource='Prometheus',
    linewidth=2,
    format='percentunit',
    decimals=2,
    fill=0,
    aliasColors={
      Target: 'light-red',
      Current: 'light-blue',
    },
  ).addTarget(
    prometheus.target(
      std.extVar("SLO_INFO_TARGET") + '{id="$service_id"}',
      legendFormat='Target',
    )
  ).addTarget(
    prometheus.target(
      std.extVar("SLO_SUCCESS_RATIO") + '{id="$service_id"}',
      legendFormat='Current',
    )
  );

local errorBudgetLeftGraph = 
  graphPanel.new(
    title='Error Budget Left',
    datasource='Prometheus',
    linewidth=2,
    format='percentunit',
    decimals=2,
    fill=100,
    aliasColors={
      'Error Budget left over SLO period': 'light-green',
    },
  ).addTarget(
    prometheus.target(
      '((1 - scalar(' + std.extVar("SLO_INFO_TARGET") + '{id="$service_id"})' + ') - (sum(increase(' + std.extVar("SLO_TOTAL_QUERY") + '['+std.extVar("SLO_WINDOW") +'])) - sum(increase(' + std.extVar("SLO_GOOD_QUERY") + '['+std.extVar("SLO_WINDOW") +'])) or vector(0)) / sum(increase(' + std.extVar("SLO_TOTAL_QUERY") + '['+std.extVar("SLO_WINDOW") +']))) / (1- scalar(' + std.extVar("SLO_INFO_TARGET") + '{id="$service_id"}))',
      legendFormat='Error Budget left over SLO period',
    )
  );

dashboard.new(
  'Service SLO',
  tags=['prometheus'],
  schemaVersion=18,
  editable=true,
  time_from='now-1d',
  refresh='1m',
)
.addTemplate(
  template.datasource(
    'PROMETHEUS_DS',
    'prometheus',
    'Prometheus',
    hide='label',
  )
)
.addTemplate(
  template.new(
    'instance',
    '$PROMETHEUS_DS',
    'label_values(prometheus_build_info, instance)',
    label='Instance',
    refresh='time',
  )
)
.addTemplate(
  template.new(
    'service_id',
    '$PROMETHEUS_DS',
    'label_values(id)',
    label='Service ID',
  )
)

.addPanels(
  [
    sloTarget { gridPos: { h: 4, w: 3, x: 0, y: 0 } },

    sloWindow { gridPos: { h: 4, w: 4, x: 3, y: 0 } },

    sloSuccessRatioGraph { gridPos: { h: 8, w: 7, x: 0, y: 4 } },

    errorBudgetLeftGraph { gridPos: { h: 12, w: 14, x: 7, y: 0 } },
  ]
)
