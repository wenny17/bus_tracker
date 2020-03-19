import json
from enum import Enum

import jsonschema


with open("schemes.json") as f:
    __schemes = json.load(f)


class Schemes(Enum):
    WINDOW_BOUNDS_SCHEMA = "window_bounds_schema"
    BUS_DATA_SCHEMA = "bus_data_schema"


class ValidationError(TypeError):
    pass


def validate_data(data, schema):
    json_data = json.loads(data)
    try:
        jsonschema.validate(instance=json_data, schema=__schemes[schema.value])
    except jsonschema.exceptions.ValidationError:
        raise ValidationError("json does not match the scheme")
    return json_data
