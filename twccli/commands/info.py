# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
import re
import datetime
import jmespath
from twccli.twcc.session import Session2
from twccli.twcc.services.base import acls, Users, image_commit, Keypairs, projects


# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# @click.group(context_settings=CONTEXT_SETTINGS, help="LiSt your TWCC resources.", cls=CatchAllExceptions(click.Command, handler=handle_exception))
@click.group(context_settings=CONTEXT_SETTINGS, help="LiSt your TWCC resources.")
def cli():
    # keyring = Keypairs()
    # ans = keyring.list()
    # if 'message' in ans:
    #     jpp(ans)
    #     exit(1)
    pass

@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")

@click.command(help="Get your HFS Information.")
@click.pass_context
def hfs(ctx, is_table):
    """Command line for info hfs

    """
    user = Users()
    user.getHFS(is_table)
@click.option(
    '-all',
    '--show-all',
    'is_all',
    is_flag=True,
    type=bool,
    help="List all the containers in the project. (Tenant Administrators only)"
)
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
            is_flag=True, default=True, show_default=True,
            help="Show information in Table view or JSON view.")

@click.command(help="Get your HFS Information.")
@click.pass_context
def proj(ctx, is_all, is_table):
    """Command line for info hfs

    """
    proj = projects()
    proj.getProjects(is_all,is_table)
    
    


cli.add_command(hfs)
cli.add_command(proj)


def main():
    cli()


if __name__ == "__main__":
    main()
