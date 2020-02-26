# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from twcc.util import pp, table_layout, SpinCursor, isNone
from twcc.services.base import acls, users, image_commit, Keypairs
from twcc.services.s3_tools import S3
from twcc.services.compute import GpuSite as Sites

def del_cntr(con_ids):
    a = Sites()
    if type(con_ids) == type(1):
        con_ids = [con_ids]
    if len(list(con_ids)) > 0:
        for con_id in con_ids:
            a.delete(con_id)
            print("Successfully remove {}".format(con_id))
    else:
        print("Need to enter Container ID")

def del_bucket(bucket_name, df):
    s3 = S3()
    s3.del_bucket(bucket_name, df)

def getConfirm(res_name, entity_name, isForce):
    if isForce:
        return isForce
    return yes_no_dialog(
        title='Confirm delete {}:[{}]'.format(res_name, entity_name),
        text='NOTICE: This action will not be reversible! \nAre you sure?').run()

def del_keypair(key_name, isForce=False):
    if getConfirm("Keypair", key_name, isForce):
        keyring = Keypairs()
        if 'name' in keyring.queryById(key_name):
            print("Keypair: {} deleted.".format(key_name))
            keyring.delete(key_name)
        else:
            raise ValueError("Keypair: {}, not found.".format(key_name))
# Create groups for command
@click.group(help="test")
def cli():
    pass

@click.option('-key', '--keypair', 'res_property', flag_value='Keypair',
              help="Delete existing keypair(s) for VCS.")
@click.option('--n', '--name', 'name', help='Name of the VCS.')
@click.option('--force / --noforce', 'force', is_flag=True,
              help='Force to delete any resource at your own cost.')
@click.argument('ids_or_names', nargs=-1)
@click.command(help="abbr for vcs")
def v(res_property, name , ids_or_names, force):
    if res_property == "Keypair":
        if not isNone(name):
            del_keypair(name, force)
    if len(ids_or_names)>0:
         for ele in ids_or_names:
              del_keypair(ele, force)

@click.command(help="abbr for cos")
def o():
    if not name:
        print('please enter bucket_name')
    else:
        print('enter remove bucket name')
        del_bucket(name, r)


@click.command(help="abbr for cntr")
@click.argument('ids_or_names', nargs=-1)
def c(ids_or_names):

    if not id:
         print('res_types {} ,con id empty'.format(ids_or_names))
    else:
         del_cntr(ids_or_names)




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
