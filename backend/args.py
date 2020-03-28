import argparse

RECEIVE_PORT = 8080
SEND_PORT = 8000


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-bus_port",
        type=int,
        default=RECEIVE_PORT,
        help="port for receiving data"
    )

    parser.add_argument(
        "-browser_port",
        type=int,
        default=SEND_PORT,
        help="port for sending data to frontend"
    )

    parser.add_argument(
        "-l",
        "--logging",
        action='store_true',
        default=False,
        help="enable logging"
    )

    return parser.parse_args()
