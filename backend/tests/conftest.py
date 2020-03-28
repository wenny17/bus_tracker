from functools import partial

from trio_websocket import serve_websocket, open_websocket_url
import pytest

from backend.server import listen_bus_route_data, handle_browser_connection


@pytest.fixture(scope="function")
async def bus_data_stream(nursery):
    await nursery.start(
        partial(serve_websocket, listen_bus_route_data, "127.0.0.1", 8080, ssl_context=None)
    )
    async with open_websocket_url("ws://127.0.0.1:8080") as ws:
        yield ws


@pytest.fixture(scope="function")
async def client_stream(nursery):

    await nursery.start(
        partial(serve_websocket, handle_browser_connection, "127.0.0.1", 8000, ssl_context=None)
    )
    async with open_websocket_url("ws://127.0.0.1:8000") as ws:
        yield ws
