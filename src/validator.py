import os
import logging
from logging import log

import requests
from jsonschema import validate
from jsonschema.validators import RefResolver
from jsonschema import ValidationError, SchemaError
from slo import OPENSLO_SCHEMA_FILES, COMMIT_SHA_OPENSLO_SCHEMA


class Validator():
    def __init__(self):
        self.schemastore = self.loadSchemaFromGithub()

    def validate_spec(self, json_data, schema_id):
        """
        load the json file and validate against loaded schema
        """
        try:
            schema = self.schemastore.get("https://openslo.com/schemas/v1/parts/%s" % schema_id)
            resolver = RefResolver("https://openslo.com",
                                   schema, self.schemastore)
            validate(json_data, schema, resolver=resolver)
        except ValidationError as error:
            return (False, error)
        except SchemaError as error:
            return (False, error)
        return True, None

    def loadSchemaFromGithub(self):
        schemastore = {}
        for schema_id in OPENSLO_SCHEMA_FILES:
            url = ('https://raw.githubusercontent.com/OpenSLO/OpenSLO/',
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
