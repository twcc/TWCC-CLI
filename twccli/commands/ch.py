# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
# , pp, jpp, table_layout, SpinCursor, isNone,
from twccli.twcc.util import mk_names
from twccli.twccli import pass_environment, logger
from twccli.twcc.services.compute_util import change_vcs, change_volume, change_loadbalancer

# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="Change your TWCC resources.")
def cli():
    pass


#@click.command(
#    help="'Change' details of your VCS (Virtual Compute Service) instances.")
#@click.option('-s', '--site-id', 'name', type=int, help="ID of the instance.")
#@click.option('-sts', '--vcs-status', type=click.Choice(['Ready', 'Stop'], case_sensitive=False), help="Status of the instance.")
#@click.option('-table / -json',
#              '--table-view / --json-view',
#              'is_table',
#              is_flag=True,
#              default=True,
#              show_default=True,
#              help="Show information in Table view or JSON view.")
#@click.option('-wait', '--wait', 'wait',
#              is_flag=True, default=False, flag_value=True,
#              help='Wait until your instance to be provisioned.')
#@click.argument('site_ids_or_names', nargs=-1)
#@pass_environment
#@click.pass_context
#def vcs(ctx, env, vcs_status, site_ids_or_names, name, wait, is_table):
#    """Command line for Change VCS
#
#    :param name: Enter name for your resources.
#    :type name: string
#    :param site_ids_or_names: list of site id
#    :type site_ids_or_names: string or tuple
#    :param vcs_status: Enter status for your resources.
#    :type vcs_status: string
#    :param wait: Wait until resources are provisioned
#    :type wait: bool
#    :param is_table: Set this flag table view or json view
#    :type is_table: bool
#    """
#    site_ids_or_names = mk_names(name, site_ids_or_names)
#    change_vcs(site_ids_or_names, str(vcs_status).lower(), is_table, wait)


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
def bss(ctx, env, name, ids_or_names, vol_status, vol_size, site_id, wait, is_table):
    """Command line for list bss

    :param name: Enter name for your volume.
    :type name: string
    :param ids_or_names: list of site id
    :type ids_or_names: string or tuple
    :param vol_status: Enter status for your volume.
    :type vol_status: string
    :param name: Enter id for your volume.
    :type name: string
    :param vol_size: Enter size for your volume.
    :type vol_size: int
    :param wait: Wait until resources are provisioned
    :type wait: bool
    :param is_table: Set this flag table view or json view
    :type is_table: bool
    """
    ids_or_names = mk_names(name, ids_or_names)
    if vol_status == None:
        click.echo('you should input --vol-status')
    if vol_status == 'extend' and vol_size == None:
        click.echo('you should input -sz, must be greater than current size')
    else:
        change_volume(ids_or_names, vol_status,
                      site_id, is_table, vol_size, wait)

@click.option('-m', '--member', type=str,
              help="Index of the volume.")
@click.option('-id', '--vlb-id', 'vlb_id', type=str,
              help="Index of the volume.")
@click.option('-lm', '--lb_method', type=click.Choice(['SOURCE_IP', 'LEAST_CONNECTIONS', 'ROUND_ROBIN'], case_sensitive=False),
              help="Method of the load balancer.")
# @click.option('-ln', '--listener-name', 'listener_name', type=str,multiple=True,
#               help="listener name of the load balancer.")
@click.option('-wait', '--wait', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your instance to be provisioned.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('more_members', nargs=-1)
@click.command(help="Update status of your vlb.")
@pass_environment
def vlb(env, vlb_id, member, more_members, lb_method, wait, is_table): #listener_name
    """Command line for list vlb

    :param vlb_id: Enter id for your load balancer.
    :type vlb_id: string
    :param member: Enter member for your load balancer.
    :type member: string
    :param more_members: more than one member
    :type more_members: string
    :param lb_methods: Enter mehtod for your load balancer.
    :type lb_methods: string
    :param wait: Wait until resources are provisioned
    :type wait: bool
    :param is_table: Set this flag table view or json view
    :type is_table: bool

    example: 'twccli ch vlb -m 1.1.1.1:80  2.2.2.2:50'
    """

    members = mk_names(member, more_members)
    change_loadbalancer(vlb_id,members,lb_method,is_table)

#cli.add_command(vcs)
cli.add_command(bss)
cli.add_command(vlb)


def main():
    cli()


if __name__ == "__main__":
    main()
