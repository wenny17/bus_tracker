import json
from functools import partial

import trio
from trio_websocket import serve_websocket, ConnectionClosed

from entities import Bus, WindowBounds

buses = {}

i = 0
async def listen_bus_route_data(request):
    """
    Get data about buses position from web socket
    """
    global i
    web_socket = await request.accept()
    while True:
        try:
            bus_data = json.loads(await web_socket.get_message())
            buses[bus_data["busId"]] = Bus(**bus_data)
            i += 1
        except ConnectionClosed:
            break


async def _listen_browser(web_socket, bounds):
    while True:
        windows_bounds = json.loads(await web_socket.get_message())
        bounds.update(**windows_bounds["data"])


async def send_buses(web_socket, bounds):
    buses_inside = [bus_info.to_dict() for bus_info in buses.values() if bounds.is_inside(bus_info.lat, bus_info.lng)]
    await web_socket.send_message(json.dumps({
        "msgType": "Buses",
        "buses": buses_inside
    }))


async def _talk_to_browser(web_socket, bounds):
    global i
    while True:
        await send_buses(web_socket, bounds)
        print(i)
        i = 0
        await trio.sleep(1)


async def handle_browser_connection(request):
    bounds = WindowBounds()
    web_socket = await request.accept()
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(_listen_browser, web_socket, bounds)
            nursery.start_soon(_talk_to_browser, web_socket, bounds)
    except ConnectionClosed:
        await trio.sleep(1)


async def main():
    open_data_socket = partial(serve_websocket, listen_bus_route_data, "127.0.0.1", 8080, ssl_context=None)
    open_browser_socket = partial(serve_websocket, handle_browser_connection, "127.0.0.1", 8000, ssl_context=None)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(open_data_socket)
        nursery.start_soon(open_browser_socket)


if __name__ == "__main__":
    trio.run(main)
