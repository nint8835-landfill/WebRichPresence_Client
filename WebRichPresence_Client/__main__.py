import json
import os
import logging

import click

from .Client import Client

logging.basicConfig(format="{%(asctime)s} (%(name)s) [%(levelname)s]: %(message)s",
                    datefmt="%x, %X",
                    level=logging.INFO)


@click.group(invoke_without_command=True)
@click.option("--port", default=80, help="Port that the WebRichPresence server is running on.")
@click.option("--hostname", default="webrichpresence.argonskyline.com", help="Hostname the WebRichPresence server is running on.")
@click.option("--config", default=os.path.join(os.path.expanduser("~"), ".webrichpresence_config.json"), help="Location of the WebRichPresence client config to use.")
@click.pass_context
def run(ctx, port, hostname, config):
    """
    Connects to a WebRichPresence server and proxies presence updates to the local Discord client.
    """
    if ctx.invoked_subcommand is None:
        client = Client(port, hostname, config)
        client.run()


@run.command()
@click.option("--config", default=os.path.join(os.path.expanduser("~"), ".webrichpresence_config.json"), help="Location of the WebRichPresence client config to use.")
def token(config):
    """
    Prints token from a given config file to the console.
    """
    if not os.path.isfile(config):
        print("Given config file does not exist!")

    with open(config) as f:
        cfg = json.load(f)

    print(f"Your token is: {cfg['token']}")
