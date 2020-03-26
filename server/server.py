import asyncio
import json
import socket

from aiohttp import web
import uvloop

from entities import WindowBounds


buses = {}

i = 0
async def listen_browser(ws, bounds):
    while True:
        async for msg in ws:
            bounds.update(**json.loads(msg.data)["data"])


async def talk_to_browser(ws, bounds):
    global i
    while True:
        buses_inside = [bus_info for bus_info in buses.values() if bounds.is_inside(bus_info["lat"], bus_info["lng"])]
        data = {
            "msgType": "Buses",
            "buses": buses_inside
        }
        await ws.send_str(json.dumps(data))
        print(i)
        i = 0
        await asyncio.sleep(1)


async def websocket_handler(request):
    print("Accept connection")
    ws = web.WebSocketResponse()
    bounds = WindowBounds()

    await ws.prepare(request)
    await asyncio.gather(
        listen_browser(ws, bounds),
        talk_to_browser(ws, bounds)
    )
    print('websocket connection closed')
    return ws


async def socket_server(reader, writer):
    global i
    try:
        while True:
            data = await reader.readline()
            message = data.decode()
            bus = json.loads(message)
            buses[bus["busId"]] = bus
            i += 1
    except (socket.gaierror,
            ConnectionRefusedError,
            ConnectionResetError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def _start_background_tasks(app):
    await asyncio.start_server(socket_server, '127.0.0.1', 8080)



def main():
    app = web.Application()
    app.on_startup.append(_start_background_tasks)
    app.add_routes([web.get('/ws', websocket_handler)])
    web.run_app(app, host="127.0.0.1", port=8000)


if __name__ == '__main__':
    uvloop.install()
    main()
