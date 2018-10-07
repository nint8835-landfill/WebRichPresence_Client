import os
import logging

import click

from .Client import Client

logging.basicConfig(format="{%(asctime)s} (%(name)s) [%(levelname)s]: %(message)s",
                    datefmt="%x, %X",
                    level=logging.INFO)


@click.command()
@click.option("--port", default=7200, help="Port that the WebRichPresence server is running on.")
@click.option("--hostname", default="localhost", help="Hostname the WebRichPresence server is running on.")
@click.option("--config", default=os.path.join(os.path.expanduser("~"), ".webrichpresence_config.json"), help="Location of the WebRichPresence client config to use.")
def run(port, hostname, config):
    client = Client(port, hostname, config)
    client.run()
