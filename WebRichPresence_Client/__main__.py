import click

@click.command()
@click.option("--port", default=7200, help="Port that the WebRichPresence server is running on.")
@click.option("--hostname", default="localhost", help="Hostname the WebRichPresence server is running on.")
def run(port, hostname):
    print(port, hostname)

