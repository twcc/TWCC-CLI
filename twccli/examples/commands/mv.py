# -*- coding: utf-8 -*-
from __future__ import print_function
import click

def Snapshots(show_list, id_num):

    snapshots_info = snapshots('sys', debug=False)
    if show_list:
        pp(list=snapshots_info.list())
    elif type(id_num) is not type(None):
        pp(list=snapshots_info.queryById(id_num))
# end original ===============================================

# Create groups for command
@click.group(help="Make copy")
def cli():
    pass

@click.command(help="Abbreviation for Virtual Compute Service")
def v():
    print("list vcs")

@click.command(help="Abbreviation for Cloud Object Storage")
@click.option('-l', '--list', 'show_list', is_flag=True, help="Show list of snapshots")
@click.option('-id', 'id_num', default=None, help="The snapshot id")
def o():
    Snapshots(show_list, id_num)

@click.command(help="Abbreviation for Container")
def c():
    print("move container")

cli.add_command(v)
cli.add_command(o)
cli.add_command(c)



def main():
    cli()


if __name__ == "__main__":
    main()
