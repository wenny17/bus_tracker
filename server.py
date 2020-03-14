import json
from functools import partial

import trio
from trio_websocket import serve_websocket, ConnectionClosed


data = {
  "msgType": "Buses",
  "buses": [
    {"busId": "c790сс", "lat": 55.7500, "lng": 37.600, "route": "120"},
    {"busId": "a134aa", "lat": 55.7494, "lng": 37.621, "route": "670к"},
  ]
}
with open("busRoute.json", "r") as f:
    DATA = json.loads(f.read())

coordinates = (x for x in DATA["coordinates"])


async def listen_bus_route_data(request):
    """
    Get data about buses route from web socket
    """
    sock = await request.accept()
    while True:
        try:
            bus_route = await sock.get_message()
            print(bus_route)
        except ConnectionClosed:
            break


async def listen_browser(request):
    ws = await request.accept()
    while True:
        try:
            #message = await ws.get_message()
            for lat, lng in coordinates:
                data = json.dumps({
                    "msgType": "Buses",
                    "buses": [
                        {"busId": "156-0", "lat": lat, "lng": lng, "route": DATA["name"]},
                    ]
                })
                await ws.send_message(data)
                await trio.sleep(1)
            raise Exception
        except ConnectionClosed:
            break


async def main():
    open_data_socket = partial(serve_websocket, listen_bus_route_data, "127.0.0.1", 8080, ssl_context=None)
    #open_browser_socket = partial(serve_websocket, listen_browser, "127.0.0.1", 8000, ssl_context=None)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(open_data_socket)
        # nursery.start_soon(open_browser_socket)


if __name__ == "__main__":
    trio.run(main)
