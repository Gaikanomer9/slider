import os
import logging
from logging import log

import requests
from jsonschema import validate
from jsonschema.validators import RefResolver
from jsonschema import ValidationError, SchemaError
from slo import SLO, OPENSLO_SCHEMA_FILES, COMMIT_SHA_OPENSLO_SCHEMA


class Validator():
    def __init__(self, load_schema=False):
        if load_schema:
            self.schemastore = self.load_schema_github()

    def validate_spec(self, json_data, schema_id):
        """
        load the json file and validate against loaded schema
        """
        try:
            schema = self.schemastore.get(
                "https://openslo.com/schemas/v1/parts/%s" % schema_id)
            resolver = RefResolver("https://openslo.com",
                                   schema, self.schemastore)
            validate(json_data, schema, resolver=resolver)
        except ValidationError as error:
            raise error
        except SchemaError as error:
            raise error
        return True

    def load_schema_github(self):
        schemastore = {}
        for schema_id in OPENSLO_SCHEMA_FILES:
            url = ('https://raw.githubusercontent.com/OpenSLO/OpenSLO/'
                   f'{COMMIT_SHA_OPENSLO_SCHEMA}/schemas/v1/{schema_id}')
            url = "".join(url)
            try:
                schema = requests.get(url).json()
            except Exception as err:
                log(logging.ERROR, f'Failed to fetch the url {url}')
                log(logging.ERROR, str(err))
                os._exit(1)
            if "$id" in schema:
                schemastore[schema["$id"]] = schema
        return schemastore

    def validate_slo(self, slo: SLO):
        if slo.kind != "SLO":
            raise ValueError(
                f'Only SLO kind is supported. Received {slo.kind}')
        windows = slo.spec.timeWindow
        objectives = slo.spec.objectives
        if len(windows) != 1 or len(objectives) != 1:
            raise ValueError(
                'Objectives and timeWindow list should contain'
                ' exactly 1 item each in the array.'
            )
        if (windows[0].isRolling is False):
            raise ValueError(
                'The only time window option supported now'
                ' is the rolling. Parameter isRolling should be set'
                ' to true and calendar should be omitted'
            )
        if (slo.spec.indicator.ratioMetric is None
           and slo.spec.indicator.thresholdMetric is None):
            raise ValueError(
                'At least of indicators should be specified: '
                'ratioMetric or thresholdMetric objects'
            )


# import yaml
# from yaml import Loader
# from slo import build_slo_from_yaml
# from rules import generate_rules

# vld = Validator()
# with open("tests/test1-openslo.yaml") as f2:
#     docs = yaml.load_all(f2, Loader)
#     for doc in docs:
#         sloObject = build_slo_from_yaml(doc)
#         vld.validate_slo(sloObject)
#         generate_rules(sloObject)