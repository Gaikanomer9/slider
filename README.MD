# SLIDER – _SLI_ *D*ashboards, *E*valuation and Ale*R*ting

Slider is a CLI tool that creates Prometheus recording and alerting rules and Grafana dashboard configs based on provided SLO specifications in [OpenSLO](https://openslo.com/) format.

## System

Current status - CLI can load and validate OpenSLO specification and pass object to the rules generator.
Rules generator is yet to be implemented.

### Installing CLI

To get started make sure you have Python 3 installed.
Install the tool in the current environment (venv recommended):

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install --editable .
```

### Usage

Some example SLOs are provided in the examples directory. To get started run:

```
slider generate tests/input/test1.yaml
```

To verify run:

```
slider verify tests/input/test1.yaml
```

Or run `slider g examples` to load specs from the directory and all subdirectories.

### Working with Docker image

First, create a local image:

```
make build_image
```

After that add a new alias to your .bashrc or command line config file:

```
alias slider="docker run -it -v $(pwd):/app/workdir:Z --rm slider"
```

After that you can use Slider without installation but because your current pwd would be attached as volume in container, make sure test files you submit are in the subdirectories and your provide absolute paths to them. For example,

```
# running this from the root directory of this repo
slider --config dashpath $(pwd)/playground/grafana/provisioning/dashboards/table.json g $(pwd)/tests/input/test1.yaml
```

### Working with dashboards

For Grafana dashboard generation the jsonnet templating engine is used as an official and recommended way of working with Grafana dashboards programmatically.

To get started, execute the slider generation command:

```
cd src
slider --config dashpath playground/grafana/provisioning/dashboards/table.json g tests/input/test1.yaml
```

Then spin up the local Prometheus stack with a sample service, you would need to clone the test app and start the services:

```
cd ../.. # make sure to be in the directory that is above slider
git clone git@github.com:Gaikanomer9/prometheus-fake-exporter.git
cd slider/playground
make run
```

This would build a new service from the app cloned. This enables quick changes on the service for testing.

Navigate to localhost:3000 and check the imported dashboard.
