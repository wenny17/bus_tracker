import itertools
import json
import os
import random


def load_routes(routes_number=None, directory_path="routes"):
    if routes_number is None:
        routes_number = len(os.listdir(directory_path))
    for filename in os.listdir(directory_path)[:routes_number]:
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


def coordinate_generator(coordinates, offset=0):
    while True:
        for coord in itertools.islice(coordinates, offset, None):
            yield coord
        offset = 0


def get_route_generator(route):
    offset = random.randint(0, len(route))
    return coordinate_generator(route, offset)


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"
