# slidergen

Slidergen is the CLI tool that creates Prometheus alerts and rules on the given OpenSLO specification files.

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
slidergen generate ../examples/slo-getting-started.yaml
```

Or run `slidergen generate ../examples` to load specs from the directory and all subdirectories.
