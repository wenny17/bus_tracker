from sys import stderr
import json
import os

import trio
from trio_websocket import open_websocket_url

BUS_DATA_PATH = 'routes'


def load_routes(directory_path=BUS_DATA_PATH):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


async def send_bus_coordinates(route):
    route_name = route["name"]
    # start_station = route["station_start_name"]
    # end_station = route["station_stop_name"]
    # route_stations = route["stations"]
    coordinates = (x for x in route["coordinates"])
    try:
        async with open_websocket_url('ws://127.0.0.1:8080') as ws:
            for lat, lng in coordinates:
                await ws.send_message(json.dumps(
                    {"busId": route_name, "lat": lat, "lng": lng, "route": route_name}, ensure_ascii=False)
                )
                await trio.sleep(.1)
    except OSError as ose:
        print('Connection attempt failed: %s' % ose, file=stderr)


async def main():
    async with trio.open_nursery() as nursery:
        for route in load_routes():
            nursery.start_soon(send_bus_coordinates, route)


if __name__ == '__main__':
    trio.run(main)


