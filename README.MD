# SLIDER – *SLI* *D*ashboards, *E*valuation and Ale*R*ting

Slider is a CLI tool that creates Prometheus recording and alerting rules and Grafana dashboard configs based on provided SLO specifications in [OpenSLO](https://openslo.com/) format.

## System

Current status - CLI can load and validate OpenSLO specification and pass object to the rules generator.
Rules generator is yet to be implemented.

### Installing CLI

To get started make sure you have Python 3 installed.
Install the tool in the current environment (venv recommended):

```
cd src
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install --editable .
```

### Usage

Some example SLOs are provided in the examples directory. To get started run:

```
slider gen ../examples/slo-getting-started.yaml
```

Or run `slider gen ../examples` to load specs from the directory and all subdirectories.
