from sys import stderr
import json
from functools import partial
import contextlib

import trio
from trio_websocket import open_websocket_url

from args import get_args
from tools import load_routes, get_route_generator, generate_bus_id, reconnect


async def run_bus(route, bus_id, route_name, send_channel, timeout=1):
    global dd
    async with send_channel:
        for lat, lng in route:
            bus_data = json.dumps({"busId": bus_id, "lat": lat, "lng": lng, "route": route_name}, ensure_ascii=False)
            await send_channel.send(bus_data)
            await trio.sleep(.1)


@reconnect
async def send_updates(server_address, receive_channel):
    client_stream = await trio.open_tcp_stream("127.0.0.1", 8080)
    async with client_stream:
        print("sender: started!")
        async for data in receive_channel:
            await client_stream.send_all(data.encode() + b"\n")



async def handle_dispatch(buses_per_route, routes_number, server_address, websocket_count=5, refresh_timeout=1):
    async with trio.open_nursery() as nursery:
        send_channel, receive_channel = trio.open_memory_channel(0)
        async with send_channel, receive_channel:
            for route_info in load_routes(routes_number):
                for bus_index in range(buses_per_route):
                    route = get_route_generator(route_info["coordinates"])
                    bus_id = generate_bus_id(route_info["name"], bus_index)

                    nursery.start_soon(run_bus, route, bus_id, route_info["name"], send_channel.clone(),
                                       refresh_timeout)

            for worker in range(websocket_count):
                nursery.start_soon(send_updates, server_address, receive_channel.clone())


if __name__ == '__main__':
    args = get_args()

    partial_handle_dispatch = partial(
        handle_dispatch,
        args.buses_per_route,
        args.routes_number,
        args.server,
        args.websockets_number,
        args.refresh_timeout
    )
    with contextlib.suppress(KeyboardInterrupt):
        trio.run(partial_handle_dispatch)
