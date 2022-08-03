import json
import logging
from logging import log
import yaml
from yaml import Loader
from jsonschema import validate
from pathlib import Path
import requests

from jsonschema.validators import RefResolver
from jsonschema import ValidationError, SchemaError
import re 
import os

COMMIT_SHA_OPENSLO_SCHEMA="ca2b59332b6fed9814f1b466877859b4ef68cb2b"
OPENSLO_SCHEMA_FILES = (
    "openslo.schema.json",
    "parts/alertcondition-spec.schema.json",
    "parts/alertnotificationtarget-spec.schema.json",
    "parts/alertpolicy-spec.schema.json",
    "parts/datasource-spec.schema.json",
    "parts/description.schema.json",
    "parts/duration-shorthand.schema.json",
    "parts/general.schema.json",
    "parts/metadata.schema.json",
    "parts/metricsource.schema.json",
    "parts/name.schema.json",
    "parts/service-spec.schema.json",
    "parts/sli-spec.schema.json",
    "parts/slo-spec.schema.json",
    
)





        

class Validator():
    def __init__(self):
        self.schemastore = self.loadSchemaFromGithub()

    def validate_spec(self, json_data, schema_id):
        """
        load the json file and validate against loaded schema
        """
        try:
            schema = self.schemastore.get("https://openslo.com/schemas/v1/parts/%s" % schema_id)
            resolver = RefResolver("https://openslo.com", schema, self.schemastore)
            validate(json_data, schema, resolver=resolver)
        except ValidationError as error:
            return (False, error)
        except SchemaError as error:
            return (False, error)
        return True, None

    
    def loadSchemaFromGithub(self):
        schemastore = {}
        for schema_id in OPENSLO_SCHEMA_FILES:
            url = f'https://raw.githubusercontent.com/OpenSLO/OpenSLO/{COMMIT_SHA_OPENSLO_SCHEMA}/schemas/v1/{schema_id}'
            try:
                schema = requests.get(url).json()
            except Exception as err:
                log(logging.ERROR, f'Failed to fetch the url {url}')
                log(logging.ERROR, str(err))
                os._exit(1)
            if "$id" in schema:
                schemastore[schema["$id"]] = schema
        return schemastore





"""
**************************
Code below is expiremental
**************************
"""


def validateSpecFromLocal(schema_search_abs_path, json_data, schema_id):
    """
    load the json file and validate against loaded schema
    """
    try:
        schemastore = loadSchemaFromFiles(schema_search_abs_path)
        schema = schemastore.get("https://openslo.com/schemas/v1/parts/%s" % schema_id)

        resolver = RefResolver("file:/%s" % os.path.join(schema_search_abs_path, schema_id), schema, schemastore)
        validate(json_data, schema, resolver=resolver)
        return True
    except ValidationError as error:
        print(error)
        # handle validation error 
        pass
    except SchemaError as error:
        print(error)
        # handle schema error
        pass
    return False


def loadSchemaFromFiles(schema_search_abs_path: str) -> dict:
    schemastore = {}
    schema = None
    fnames = os.listdir(schema_search_abs_path)
    fnames = [os.path.join(schema_search_abs_path, p) for p in fnames]
    for fname in fnames:
        fpath = os.path.join(schema_search_abs_path, fname)
        if os.path.isdir(fpath):
            sub_fnames = os.listdir(fpath)
            sub_fnames = [os.path.join(fpath, p) for p in sub_fnames]
            fnames.extend(sub_fnames)
        if fpath[-5:] == ".json":
            with open(fpath, "r") as schema_fd:
                schema = json.load(schema_fd)
                if "$id" in schema:
                    schemastore[schema["$id"]] = schema
    return schemastore



    

# with open("examples/slo-getting-started.yaml") as f2:
#     testSLO = yaml.load(f2, Loader)

# if validate_spec(testSLO, "slo-spec.schema.json"):
#     print("Schema was valid")

# with open("examples/slo-getting-started.yaml") as f2:
#     testSLO = yaml.load(f2, Loader)

# if validateSpecFromLocal(os.getcwd()+"/OpenSLO", testSLO, "slo-spec.schema.json"):
#     print("Schema was valid")
