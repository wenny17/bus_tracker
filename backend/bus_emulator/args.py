import argparse
import os


SERVER_ADDRESS = 'ws://127.0.0.1:8080'
BUSES_PER_ROUTE = 2
WEBSOCKET_COUNT = 5
UPDATE_TIMEOUT = 1

try:
    ROUTES_NUMBER = len(os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "routes/")))
except FileNotFoundError as e:
    message = "Add the 'routes/' directory  which contains the buses coordinates data"
    raise type(e)(e.strerror + "\n\t" + message)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-server",
        type=str,
        default=SERVER_ADDRESS,
        help="address of backend which accepts the emulator data"
    )

    parser.add_argument(
        "-r",
        "--routes_number",
        type=int,
        default=ROUTES_NUMBER,
        help="number of buses routes"
    )

    parser.add_argument(
        "-b",
        "--buses_per_route",
        type=int,
        default=BUSES_PER_ROUTE,
        help="buses per route"
    )

    parser.add_argument(
        "-w",
        "--websockets_number",
        type=int,
        default=WEBSOCKET_COUNT,
        help="the number of web-sockets that connect to the backend"
    )

    parser.add_argument(
        "--emulator_id",
        type=int,
        default=0,
        help=""
    )

    parser.add_argument(
        "-t",
        "--refresh_timeout",
        type=float,
        default=UPDATE_TIMEOUT,
        help="latency in updating backend coordinates"
    )

    parser.add_argument(
        "-l",
        "--logging",
        action='store_true',
        default=False,
        help="enable logging"
    )

    return parser.parse_args()
