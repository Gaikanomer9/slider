import os
import yaml


def produce_output(output: str, filepath: str, data: any, yaml_dump_args: dict = {}):
    os.makedirs(output, exist_ok=True)
    output_path = os.path.join(output, filepath)
    with open(output_path, 'w') as f:
        yaml.dump(data, f, **yaml_dump_args)
