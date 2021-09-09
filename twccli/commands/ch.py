# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import re
import click
import json
from twccli.twcc.util import mk_names, isNone
from twccli.twccli import pass_environment, logger
from twccli.twcc.services.compute_util import change_vcs, change_ccs, change_volume, change_loadbalancer, change_ip
from twccli.twcc.services.base import acls, users, image_commit, Keypairs
from twccli.twcc.services.s3_tools import S3


# functions
def set_object_public(bkt, okey_regex, is_public=False):
    import re
    s3 = S3()
    files = s3.list_object(bkt)
    if not isNone(okey_regex):
        for mfile in files:
            if re.search(okey_regex, mfile[u'Key']):  # 會不會中招呀!?
                s3.put_obj_acl(okey=mfile[u'Key'],
                               bkt=bkt, is_public=is_public)
                print("Making bucket-name: %s, object-key: %s, %s. " %
                      (bkt, mfile[u'Key'], "public" if is_public else "non-public"))


def set_object_content_type(bkt, okey_regex, mime):
    s3 = S3()
    files = s3.list_object(bkt)
    if not isNone(okey_regex):
        for mfile in files:
            if re.search(okey_regex, mfile[u'Key']):  # 會不會中招呀!?
                s3.set_obj_contet_type(bkt, mfile[u'Key'], mime)
                print("Making bucket-name: %s, object-key: %s, %s. " %
                      (bkt, mfile[u'Key'], mime))


def set_versioning(bkt, versioning):
    s3 = S3()
    if versioning == True:
        s3.enable_versioning(bkt)
    else:
        s3.disable_versioning(bkt)


# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="Change your TWCC resources.")
def cli():
    try:
        from twccli.twcc.services.generic import GenericService
        ga = GenericService()
        func_call = '_'.join([i for i in sys.argv[1:] if re.findall(
            r'\d', i) == [] and not i == '-sv']).replace('-', '')
        ga._send_ga(func_call)
    except Exception as e:
        logger.warning(e)
    pass


@click.command(
    help="'Change' details of your VCS (Virtual Compute Service) instances.")
@click.option('-d', '--site-desc', 'desc', type=str, default='', help="Description of the instance.")
@click.option('-s', '--site-id', 'name', type=int, help="ID of the instance.")
@click.option('-keep/-nokeep', '--keep/--nokeep', 'keep', is_flag=True, default=None, help="Termination protection of the instance.")
@click.option('-sts', '--vcs-status', type=click.Choice(['Ready', 'Stop', 'Reboot'], case_sensitive=False), help="Status of the instance.")

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
def vcs(ctx, env, desc, site_ids_or_names, name, vcs_status, keep, is_table, wait):
    """Command line for Change VCS

    :param name: Enter name for your resources.
    :type name: string
    :param site_ids_or_names: list of site id
    :type site_ids_or_names: string or tuple
    :param vcs_status: Enter status for your resources.
    :type vcs_status: string
    :param wait: Wait until resources are provisioned
    :type wait: bool
    :param is_table: Set this flag table view or json view
    :type is_table: bool
    """
    site_ids_or_names = mk_names(name, site_ids_or_names)
    change_vcs(site_ids_or_names, str(
        vcs_status).lower(), is_table, desc, keep, wait)

@click.command(
    help="'Change' details of your CCS (Container Computer Service) containers.")
@click.option('-s', '--site-id', 'name', type=int, help="ID of the instance.")
@click.option('-d', '--site-desc', 'desc', type=str, default='', help="Description of the instance.")
@click.option('-keep/-nokeep', '--keep/--nokeep', 'keep', is_flag=True, default=None, help="Termination protection of the instance.")
@click.option('-table / -json',
              '--table-view / --json-view',
              'is_table',
              is_flag=True,
              default=True,
              show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('site_ids_or_names', nargs=-1)
@pass_environment
@click.pass_context
def ccs(ctx, env, desc, site_ids_or_names, name, keep, is_table):
    """Command line for Change CCS

    """
    site_ids_or_names = mk_names(name, site_ids_or_names)
    change_ccs(site_ids_or_names, is_table, desc, keep)


@click.option('-s', '--site-id', type=str, help="ID of the instance.")
@click.option('-id', '--disk-id', 'name', type=str,
              help="Index of the disk.")
@click.option('-sz', '--disk-size', 'vol_size', type=int, show_default=True,
              help="Extend size of the disk. Must be greater than current size")
@click.option('-sts', '--disk-status', 'vol_status', type=click.Choice(['attach', 'detach', 'extend'], case_sensitive=False),
              help="Status of the disk.")
@click.option('-wait', '--wait', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your instance to be provisioned.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="Update status of your VDS (Virtual Disk Service).")
@pass_environment
@click.pass_context
def vds(ctx, env, name, ids_or_names, vol_status, vol_size, site_id, wait, is_table):
    """Command line for list vds

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
              help="Change members of load balancer, ex: twccli ch vlb -id {$vlbid} -m 192.168.100.1:80 192.168.100.2:80")
@click.option('-id', '--vlb-id', 'vlb_id', type=str,
              help="Index of the load balancer.")
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
def vlb(env, vlb_id, member, more_members, lb_method, wait, is_table):  # listener_name
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
    change_loadbalancer(vlb_id, members, lb_method, is_table)


@click.option('-bkt',
              '--bucket-name',
              'name',
              default=None,
              type=str,
              help="Name of the Bucket.")
@click.option('-okey',
              '--object-key-name',
              'okey',
              default=None,
              type=str,
              help="Name of specific object key. Regular Expression compatible.")
@click.option('-pub / -nopub',
              '--set-public / --unset-public',
              'is_public',
              is_flag=True,
              default=None,
              show_default=True,
              help="Set object to public or private.")
@click.option('-mime',
              '--set-content-type',
              'mime',
              type=str,
              default=None,
              help="Set content type for object.")
@click.option('-ver / -nover',
              '--enable-versioning / --disable-versioning',
              'versioning',
              is_flag=True,
              default=None,
              help="Enabled or Disabled versioning for a bucket.")
@click.command(help="Update permission of your objects.")
@pass_environment
def cos(env, name, okey, is_public, mime, versioning):
    """Command line for change COS buckets and objects
    """

    if not isNone(mime):
        set_object_content_type(name, okey, mime=mime)
    if not isNone(is_public):
        set_object_public(name, okey, is_public=is_public)
    if not isNone(versioning):
        set_versioning(name, versioning)


@click.option('-id', '--private-net-id', 'ip_id', type=int,
              help="Index of the IP.")
@click.option('-d', '--IP-description', 'desc', type=str, default=None,
              help="Description of the IP.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="Update desc of your IP.")
@click.pass_context
def fxip(ctx, ip_id, desc, ids_or_names, is_table):
    ids_or_names = mk_names(ip_id, ids_or_names)
    change_ip(ids_or_names, desc, is_table)


cli.add_command(vcs)
cli.add_command(ccs)
cli.add_command(vds)
cli.add_command(vlb)
cli.add_command(cos)
cli.add_command(fxip)

def main():
    cli()


if __name__ == "__main__":
    main()
