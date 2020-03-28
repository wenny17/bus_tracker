import json
from functools import partial

import trio
from trio_websocket import serve_websocket, ConnectionClosed

from backend.entities import Bus, WindowBounds
from backend.validation import validate_data, ValidationError, Schemes
from backend.args import get_args


buses = {}


async def listen_bus_route_data(request):
    """
    Get data about buses position from web socket
    """
    web_socket = await request.accept()
    while True:
        try:
            data = await web_socket.get_message()
            try:
                bus_data = json.loads(data)
            except json.JSONDecodeError:
                await web_socket.send_message(json.dumps({"errors": ["Requires valid JSON"], "msgType": "Errors"}))
                continue
            try:
                # something like validation :) other solutions(especially with jsonschema) will be too slow
                bus = Bus(**bus_data)
            except TypeError:
                await web_socket.send_message(json.dumps({"errors": ["Requires busId specified"], "msgType": "Errors"}))
            else:
                buses.update({bus.busId: bus})
        except ConnectionClosed:
            break


async def listen_browser(web_socket, bounds):
    """
    get windows bounds from front-end and update bounds: WindowBounds
    """
    while True:
        data = await web_socket.get_message()
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            await web_socket.send_message(json.dumps({"errors": ["Requires valid JSON"], "msgType": "Errors"}))
            continue
        try:
            windows_bounds = validate_data(json_data, Schemes.WINDOW_BOUNDS_SCHEMA)
        except ValidationError:
            await web_socket.send_message(json.dumps({"errors": ["Requires msgType specified"], "msgType": "Errors"}))
        else:
            bounds.update(**windows_bounds["data"])


async def send_buses(web_socket, bounds):
    buses_inside = [bus_info.to_dict() for bus_info in buses.values() if bounds.is_inside(bus_info.lat, bus_info.lng)]
    await web_socket.send_message(json.dumps({
        "msgType": "Buses",
        "buses": buses_inside
    }))


async def talk_to_browser(web_socket, bounds):
    while True:
        await send_buses(web_socket, bounds)
        await trio.sleep(1)


async def handle_browser_connection(request):
    bounds = WindowBounds()
    web_socket = await request.accept()
    try:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(listen_browser, web_socket, bounds)
            nursery.start_soon(talk_to_browser, web_socket, bounds)
    except ConnectionClosed:
        await trio.sleep(1)


async def main(bus_port, browser_port):
    open_data_socket = partial(serve_websocket, listen_bus_route_data, "127.0.0.1", bus_port, ssl_context=None)
    open_browser_socket = partial(serve_websocket, handle_browser_connection, "127.0.0.1", browser_port, ssl_context=None)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(open_data_socket)
        nursery.start_soon(open_browser_socket)


if __name__ == "__main__":
    args = get_args()
    trio.run(main, args.bus_port, args.browser_port)
