# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
from twccli.twcc.util import mk_names#, pp, jpp, table_layout, SpinCursor, isNone, 

from twccli.twcc.services.compute_util import change_vcs



# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="Change your TWCC resources.")
def cli():
    pass


@click.command(
    help="'Change' details of your VCS (Virtual Compute Service) instances.")
@click.option('-s', '--site-id', 'name', type=int, help="ID of the instance.")

@click.option('-sts', '--vcs-status', type=click.Choice(['Ready', 'Stop'], case_sensitive=False), help="Status of the instance.")
@click.option('-table / -json',
              '--table-view / --json-view',
              'is_table',
              is_flag=True,
              default=True,
              show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('site_ids_or_names', nargs=-1)
@click.pass_context
def vcs(ctx, vcs_status, site_ids_or_names, name, is_table):
    """Command line for Change VCS
    Function list :
    1. Change VCS status
    """
    site_ids_or_names = mk_names(name, site_ids_or_names)
    change_vcs(site_ids_or_names,str(vcs_status).lower(),is_table,is_table)
    # if vcs_status == 'ready':
        
    # elif vcs_status == 'ready':
    #     change_vcs(site_ids_or_names,'ready')
    # click.echo(vcs_status)
    # if res_property == 'VcsStatus':
    #     click.echo(vcs_status)
    # click.echo('aa')
    


cli.add_command(vcs)


def main():
    cli()


if __name__ == "__main__":
    main()
