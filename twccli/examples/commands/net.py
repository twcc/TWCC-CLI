from twcc.services.compute import GpuSite as Sites
import click


@click.command(help='ccs(Container Compute Service)')
@click.option('-att/-unatt', '--attach-port/--unattach-port', 'isbind', is_flag=True, help='exposed/un-exposed port for continer services')
@click.option('-p', '--port', 'port', type=int, help='port nummber')
@click.option('-s', '--site-id', 'siteId', type=int, help='site id')
def c(siteId, port, isbind):
    b = Sites()
    if isbind:
        b.exposedPort(siteId, port)
    else:
        b.unbindPort(siteId, port)


@click.group(help="Network Service")
def cli():
    pass

cli.add_command(c)

def main():
    cli()

if __name__ == "__main__":
    main()
