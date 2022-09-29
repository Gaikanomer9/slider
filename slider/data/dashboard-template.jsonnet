local grafana = import '../../../grafonnet-lib/grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local template = grafana.template;
local singlestat = grafana.singlestat;
local graphPanel = grafana.graphPanel;
local prometheus = grafana.prometheus;

local sloInfo =
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

local sloRatio =
  singlestat.new(
    title='SLO Success Ratio',
    datasource='Prometheus',
    format='none',
    valueName='current',
    decimals=2,
    sparklineShow=true,
    colorValue=true,
    thresholds='4,6',
  ).addTarget(
    prometheus.target(
      'slo:success:ratio',
    )
  );

local ratioGraph =
  graphPanel.new(
    title='SLO Ratio',
    datasource='Prometheus',
    linewidth=2,
    format='percentunit',
    decimals=4,
    aliasColors={
      Target: 'light-green',
      Current: 'light-red',
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
  time_from='now-1h',
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
    sloInfo { gridPos: { h: 4, w: 3, x: 0, y: 0 } },

    sloRatio { gridPos: { h: 4, w: 4, x: 3, y: 0 } },

    ratioGraph { gridPos: { h: 8, w: 7, x: 0, y: 4 } },
  ]
)