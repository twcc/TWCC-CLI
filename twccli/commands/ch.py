# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
# , pp, jpp, table_layout, SpinCursor, isNone,
from twccli.twcc.util import mk_names
from twccli.twcc.services.compute_util import change_vcs, change_volume

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
@click.option('-wait', '--wait', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your instance to be provisioned.')
@click.argument('site_ids_or_names', nargs=-1)
@pass_environment
@click.pass_context
def vcs(ctx, env, vcs_status, site_ids_or_names, name, wait, is_table):
    """Command line for Change VCS
    Function list :
    1. Change VCS status
    """
    site_ids_or_names = mk_names(name, site_ids_or_names)
    change_vcs(site_ids_or_names, str(vcs_status).lower(), is_table, wait)


@click.option('-s', '--site-id', type=str, help="ID of the instance.")
@click.option('-id', '--vol-id', 'name', type=str,
              help="Index of the volume.")
@click.option('-sz', '--vol-size', type=int, show_default=True,
              help="Extend size of the volume. Must be greater than current size")              
@click.option('-sts', '--vol-status', type=click.Choice(['attach', 'detach', 'extend'], case_sensitive=False),
              help="Status of the volume.")
@click.option('-wait', '--wait', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your instance to be provisioned.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="Update status of your BSS.")
@pass_environment
@click.pass_context
def bss(ctx, env, name, ids_or_names, vol_status, vol_size, site_id, wait, is_all, is_table):
    """Command line for list bss

    :param name: Enter name for your resources.
    :type name: string
    """
    ids_or_names = mk_names(name, ids_or_names)
    if vol_status == None:
        click.echo('you should input --vol-status')
    if vol_status == 'extend' and vol_size == None:
        click.echo('you should input -sz, must be greater than current size')
    else:
        change_volume(ids_or_names, vol_status, site_id, is_table, vol_size, wait)


cli.add_command(vcs)
cli.add_command(bss)


def main():
    cli()


if __name__ == "__main__":
    main()
