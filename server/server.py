import json
from functools import partial

import trio
from trio_websocket import serve_websocket, ConnectionClosed

buses = {}


async def listen_bus_route_data(request):
    """
    Get data about buses route from web socket
    """
    sock = await request.accept()
    while True:
        try:
            bus_route = json.loads(await sock.get_message())
            print(bus_route)
            buses[bus_route["busId"]] = bus_route
        except ConnectionClosed:
            break


async def listen_browser(request):
    sock = await request.accept()
    while True:
        try:
            data = list(buses.values())
            await sock.send_message(json.dumps({
              "msgType": "Buses",
              "buses": data
            }))
            print(data)
            await trio.sleep(1)

        except ConnectionClosed:
            break


async def main():
    open_data_socket = partial(serve_websocket, listen_bus_route_data, "127.0.0.1", 8080, ssl_context=None)
    open_browser_socket = partial(serve_websocket, listen_browser, "127.0.0.1", 8000, ssl_context=None)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(open_data_socket)
        nursery.start_soon(open_browser_socket)


if __name__ == "__main__":
    trio.run(main)

