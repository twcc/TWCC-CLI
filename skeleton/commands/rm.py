# -*- coding: utf-8 -*-
from __future__ import print_function
import click

# Create groups for command
@click.group(help="test")
def cli():
    pass

@click.command(help="abbr for vcs")
def v():
    print("list vcs")

@click.command(help="abbr for cos")
def o():
    print("list cos")

@click.command(help="abbr for cntr")
def c():
    print("list cntr")

cli.add_command(v)
cli.add_command(o)
cli.add_command(c)



def main():
    """
    this is a test main function
    """
    cli()


if __name__ == "__main__":
    main()
