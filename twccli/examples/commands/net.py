from twcc.services.compute import GpuSite as Sites
import click


@click.command(help='Abbreviation of Container')
@click.option('-att/-unatt', '--attach/--un-attach', 'isbind', is_flag=True, help='exposed/un-exposed port for continer services')
@click.option('-p', '--port', 'port', type=int, help='number of port')
@click.option('-s', '--site', 'siteId', type=int, help='site id')
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
