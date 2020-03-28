import json
from enum import Enum
import os

import jsonschema


with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "schemes.json")) as f:
    __schemes = json.load(f)


class Schemes(Enum):
    WINDOW_BOUNDS_SCHEMA = "window_bounds_schema"
    BUS_DATA_SCHEMA = "bus_data_schema"


class ValidationError(TypeError):
    pass


def validate_data(json_data, schema):
    try:
        jsonschema.validate(instance=json_data, schema=__schemes[schema.value])
    except jsonschema.exceptions.ValidationError:
        raise ValidationError("json does not match the scheme")
    return json_data
