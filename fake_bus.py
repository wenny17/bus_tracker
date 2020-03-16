from sys import stderr
import json
import os
import itertools
import random

import trio
from trio_websocket import open_websocket_url

BUS_DATA_PATH = 'routes'


def load_routes(directory_path=BUS_DATA_PATH):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


def coordinate_generator(coordinates, offset=0):
    while True:
        for coord in (x for x in coordinates[offset:]):
            yield coord
        offset = 0


def generate_bus_data(route):
    offset = random.randint(0, len((route["coordinates"])))
    route["coordinates"] = coordinate_generator(route["coordinates"], offset)
    return route


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


# async def run_bus(route, bus_id, url='ws://127.0.0.1:8080'):
#     route_name = route["name"]
#     coordinates = route["coordinates"]
#     try:
#         async with open_websocket_url('ws://127.0.0.1:8080') as ws:
#             for lat, lng in coordinates:
#                 await ws.send_message(json.dumps(
#                     {"busId": bus_id, "lat": lat, "lng": lng, "route": route_name}, ensure_ascii=False)
#                 )
#                 await trio.sleep(1)
#     except OSError as ose:
#         print('Connection attempt failed: %s' % ose, file=stderr)
async def run_bus(route, bus_id, send_channel):
    route_name = route["name"]
    coordinates = route["coordinates"]
    async with send_channel:
        for lat, lng in coordinates:
            bus_data = json.dumps({"busId": bus_id, "lat": lat, "lng": lng, "route": route_name}, ensure_ascii=False)
            await send_channel.send(bus_data)
            await trio.sleep(1)


async def send_updates(receive_channel, server_address='ws://127.0.0.1:8080'):
    async with receive_channel:
        async with open_websocket_url(server_address) as ws:
            async for data in receive_channel:
                await ws.send_message(data)


async def main(workers=5):
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(0)
        async with send_channel, receive_channel:
            for route in load_routes():
                for bus_index in range(1):
                    nursery.start_soon(run_bus, generate_bus_data(route.copy()), generate_bus_id(route["name"], bus_index), send_channel.clone())
            for worker in range(workers):
                nursery.start_soon(send_updates, receive_channel.clone())


if __name__ == '__main__':
    trio.run(main)


