import asyncio
import json

import uvloop

from args import get_args
from tools import load_routes, get_route_generator, generate_bus_id, reconnect


async def run_bus(route, bus_id, route_name, queue, timeout=1):
    for lat, lng in route:
        bus_data = json.dumps({"busId": bus_id, "lat": lat, "lng": lng, "route": route_name}, ensure_ascii=False)
        await queue.put(bus_data)
        await asyncio.sleep(1)


@reconnect
async def send_updates(server_address, queue):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8080)
    while True:
        data = await queue.get()
        writer.write(data.encode() + b"\n")
        await writer.drain()


async def handle_dispatch(buses_per_route, routes_number, server_address, websocket_count=5, refresh_timeout=1):
    message_queue = asyncio.Queue()
    coros = []
    for route_info in load_routes(routes_number):
        for bus_index in range(buses_per_route):
            route = get_route_generator(route_info["coordinates"])
            bus_id = generate_bus_id(route_info["name"], bus_index)
            coros.append(run_bus(route, bus_id, route_info["name"], message_queue, refresh_timeout))
    await asyncio.gather(
        *coros, *[send_updates(server_address, message_queue) for _ in range(websocket_count)]
    )


if __name__ == '__main__':
    args = get_args()
    uvloop.install()
    asyncio.run(
        handle_dispatch(
            args.buses_per_route,
            args.routes_number,
            args.server,
            args.websockets_number,
            args.refresh_timeout,
        )
    )
