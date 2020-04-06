import json
from functools import partial
import logging.config
import contextlib

import trio
from trio_websocket import serve_websocket, ConnectionClosed

from entities import Bus, WindowBounds
from validation import validate_data, ValidationError, Schemes
from args import get_args


logger = logging.getLogger('server')

buses = {}


async def listen_bus_route_data(request):
    """
    Get data about buses position from web socket
    """
    web_socket = await request.accept()
    logging.debug("accept connection for bus data")
    while True:
        with contextlib.suppress(ConnectionClosed):
            data = await web_socket.get_message()
            try:
                bus_data = json.loads(data)
            except json.JSONDecodeError:
                logger.debug("received non-valid json from bus stream")
                await web_socket.send_message(json.dumps({"errors": ["Requires valid JSON"], "msgType": "Errors"}))
                continue
            try:
                # something like validation :) other solutions(especially with jsonschema) will be too slow
                bus = Bus(**bus_data)
            except TypeError:
                logger.debug("received bad schema from bus stream")
                await web_socket.send_message(json.dumps({"errors": ["Requires busId specified"], "msgType": "Errors"}))
            else:
                buses.update({bus.busId: bus})
    logger.debug("end bus data connection")


async def listen_browser(web_socket, bounds):
    """
    get windows bounds from front-end and update bounds: WindowBounds
    """
    while True:
        data = await web_socket.get_message()
        logger.info("received user window bounds from browser")
        try:
            json_data = json.loads(data)
        except json.JSONDecodeError:
            logger.debug("received non-valid json from browser")
            await web_socket.send_message(json.dumps({"errors": ["Requires valid JSON"], "msgType": "Errors"}))
            continue
        try:
            windows_bounds = validate_data(json_data, Schemes.WINDOW_BOUNDS_SCHEMA)
        except ValidationError:
            logger.debug("received bad schema from browser")
            await web_socket.send_message(json.dumps({"errors": ["Requires msgType specified"], "msgType": "Errors"}))
        else:
            bounds.update(**windows_bounds["data"])


async def send_buses(web_socket, bounds):
    buses_inside = [bus_info.to_dict() for bus_info in buses.values() if bounds.is_inside(bus_info.lat, bus_info.lng)]

    logger.debug("sending bus data to browser")
    await web_socket.send_message(json.dumps({
        "msgType": "Buses",
        "buses": buses_inside
    }))


async def talk_to_browser(web_socket, bounds):
    while True:
        await send_buses(web_socket, bounds)
        await trio.sleep(1)


async def handle_browser_connection(request):
    logger.debug("accept connection with new user")
    bounds = WindowBounds()
    web_socket = await request.accept()
    with contextlib.suppress(ConnectionClosed):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(listen_browser, web_socket, bounds)
            nursery.start_soon(talk_to_browser, web_socket, bounds)
    logger.debug("lost connection with user")


async def main(bus_port, browser_port, host):
    open_data_socket = partial(serve_websocket, listen_bus_route_data, host, bus_port, ssl_context=None)
    open_browser_socket = partial(serve_websocket, handle_browser_connection, host, browser_port, ssl_context=None)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(open_data_socket)
        nursery.start_soon(open_browser_socket)


if __name__ == "__main__":
    args = get_args().parse_args()

    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging_level = logging.DEBUG if args.verbose else logging.WARNING
    logger.setLevel(logging_level)

    with contextlib.suppress(KeyboardInterrupt):
        trio.run(main, args.bus_port, args.browser_port, args.host)
