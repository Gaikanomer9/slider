# SLIDER – _SLI_ *D*ashboards, *E*valuation and Ale*R*ting

Slider is a CLI tool that creates Prometheus recording and alerting rules and Grafana dashboard configs based on provided SLO specifications in [OpenSLO](https://openslo.com/) format.

## System

Current status – Proof of Concept.
A basic dashboard and matching recording rules can be generated, but work is needed to get them to production state.

### Quickstart

The quickest way to test out slider is by running it from a container, like this:

1. Set up an alias
    ```
    alias slider="docker run -it -v $(pwd):/app/workdir --rm quay.io/mmazur/slider"
    ```
2. Clone this repo
3. Make a test run:
    ```
    slider generate tests/input/test1.yaml
    ```
4. Inspect the newly-created `rules.yaml` and `dashboard.json` files.

> **Note**  
> If SELinux interferes with using the container, you can try this alias instead:  
> `alias slider="docker run -it -v $(pwd):/app/workdir:z --rm quay.io/mmazur/slider"`

### Usage

Some example SLOs are provided in the examples directory. To get started run:

```
slider generate tests/input/test1.yaml
```

To verify run:

```
slider verify tests/input/test1.yaml
```

Or run `slider gen examples` to load specs from the directory and all subdirectories.

### Setting up a development environment

The developers of this project use the following setup:

```
# from the project's root directory:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install --editable .
```

After these commands complete the command `venv/bin/slider` will become available and any further changes you might make to the code will be immediately reflected in its runtime behavior.


#### Building a Docker image

Creating your own docker container is as simple as invoking this command:

```
make build_image
```

> **Note**  
> Running slider from a container limits its filesystem access to the current working directory the `slider` alias is invoked from.
> If you require full filesystem access, you'll likely want to e.g. `pip install` into `/usr/local`.


### Dashboard playground

> **Note**  
> This info might be slightly out of date.

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
