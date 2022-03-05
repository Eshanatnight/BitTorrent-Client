"""
This files deals with the Command Line Interface (CLI) of the Torrenting Engine

"""

import argparse
import asyncio
from http import client
import logging
import signal

from concurrent.futures import CancelledError

from pieces.torrent import Torrent
from pieces.client import TorrentClient


def main():
    parser = argparse.ArgumentParser(description="Torrenting Engine")
    parser.add_argument("torrent", help="the torrent file to download")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    client = TorrentClient(Torrent(args.torrent))
    task = loop.create_task(client.start())

    def signal_handler(*_):
        logging.info('Exiting, please wait until everything is shutdown...')
        client.stop()
        task.cancel()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        loop.run_until_complete(task)
    except CancelledError:
        logging.warning('Event loop was canceled')
