import itertools
import json
import os
import random
import functools

import trio
from trio_websocket._impl import HandshakeError, ConnectionClosed


def load_routes(routes_number=None, directory_path="routes"):
    directory_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "routes/")
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


def _clear_channel(channel):
    for _ in range(channel.statistics().tasks_waiting_send):
        channel.receive_nowait()
    if channel.statistics().tasks_waiting_send != 0:
        raise Exception
    return channel


def reconnect(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                # if not isinstance(args[1], trio.MemoryReceiveChannel):
                #     raise TypeError("expected trio.MemoryReceiveChannel instance")
                #receive_channel = _clear_channel(args[1])
                #await f(args[0], receive_channel, **kwargs)

                await f(*args, **kwargs)
            except (HandshakeError, ConnectionClosed):
                print("RECONNECT IN 3sec...")
                await trio.sleep(3)
            else:
                args[1].aclose()

    return wrapper

# ['aclose', 'clone', 'receive', 'receive_nowait', 'statistics']
