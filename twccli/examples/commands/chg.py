# -*- coding: utf-8 -*-
from __future__ import print_function
import click

# Create groups for command
@click.group(help="Change configuration")
def cli():
    pass

@click.command(help="Abbreviation for Virual Compute Service")
def v():
    print("list vcs")

@click.command(help="Abbreviation for Cloud Object Storage")
def o():
    print("list cos")

@click.command(help="Abbreviation for container")
def c():
    print("list cntr")

cli.add_command(v)
cli.add_command(o)
cli.add_command(c)



def main():
    cli()


if __name__ == "__main__":
    main()
