import argparse

RECEIVE_PORT = 8080
SEND_PORT = 8000
HOST = '127.0.0.1'


def get_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-bus_port",
        type=int,
        default=RECEIVE_PORT,
        help="port for receiving data"
    )

    parser.add_argument(
        "-host",
        type=str,
        default=HOST,
        help="listen host"
    )

    parser.add_argument(
        "-browser_port",
        type=int,
        default=SEND_PORT,
        help="port for sending data to frontend"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action='store_true',
        default=False,
        help="enable logging"
    )

    return parser
