import itertools
import json
import os
import random
import functools
import logging.config

import trio
from trio_websocket._impl import HandshakeError, ConnectionClosed


ROUTE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "routes"
)

logger = logging.getLogger('emulator').getChild(__name__)


def load_routes(routes_number=None, directory_path=ROUTE_PATH):
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


def reconnect(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                if not isinstance(args[1], trio.MemoryReceiveChannel):
                    raise TypeError(
                        "expected trio.MemoryReceiveChannel instance"
                    )

                await f(*args, **kwargs)

            except (HandshakeError, ConnectionClosed):
                logger.warning(
                    "lost connection with server. Reconnect in 1sec..."
                )
                await trio.sleep(1)
            else:
                await args[1].aclose()

    return wrapper
