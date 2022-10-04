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
      'slo:info:target',
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
      'slo:info:target',
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
      'slo:info:target',
      legendFormat='Target',
    )
  ).addTarget(
    prometheus.target(
      'slo:success:ratio',
      legendFormat='Current',
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

.addPanels(
  [
    sloTarget { gridPos: { h: 4, w: 3, x: 0, y: 0 } },

    sloWindow { gridPos: { h: 4, w: 4, x: 3, y: 0 } },

    sloSuccessRatioGraph { gridPos: { h: 8, w: 7, x: 0, y: 4 } },
  ]
)
