import json
from functools import partial
import contextlib
import logging.config

import trio
from trio_websocket import open_websocket_url

from args import get_argparser
from tools import load_routes, get_coords_generator, generate_bus_id, reconnect


logger = logging.getLogger("emulator")


async def run_bus(coordinates, bus_id, route_name, send_channel, timeout=1):
    for lat, lng in coordinates:
        bus_data = json.dumps(
            {"busId": bus_id, "lat": lat, "lng": lng, "route": route_name},
            ensure_ascii=False
        )
        await send_channel.send(bus_data)
        await trio.sleep(timeout)


@reconnect
async def send_updates(server_address, receive_channel):
    async with open_websocket_url(server_address) as ws:
        async for data in receive_channel:
            logger.debug("sending bus data")
            await ws.send_message(data)


async def main(buses_per_route,
               routes_number,
               server_address,
               websocket_count=5,
               refresh_timeout=1):

    send_channel, receive_channel = trio.open_memory_channel(0)
    async with send_channel, receive_channel:
        async with trio.open_nursery() as nursery:
            for route in load_routes(routes_number):
                for bus_index in range(buses_per_route):
                    coords = get_coords_generator(route["coordinates"])
                    bus_id = generate_bus_id(route["name"], bus_index)

                    nursery.start_soon(run_bus, coords, bus_id, route["name"],
                                       send_channel, refresh_timeout)

            for worker in range(websocket_count):
                nursery.start_soon(send_updates, server_address,
                                   receive_channel)


if __name__ == '__main__':
    args = get_argparser().parse_args()

    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.ERROR, format=formatter)
    logging_level = logging.DEBUG if args.verbose else logging.WARNING
    logger.setLevel(logging_level)

    partial_handle_dispatch = partial(
        main,
        args.buses_per_route,
        args.routes_number,
        args.server,
        args.websockets_number,
        args.refresh_timeout
    )
    with contextlib.suppress(KeyboardInterrupt):
        trio.run(partial_handle_dispatch)
