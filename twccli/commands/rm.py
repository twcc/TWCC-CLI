# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import re
from twccli.twcc.util import pp, table_layout, SpinCursor, isNone, mk_names, isFile
from twccli.twcc.services.base import acls, users, image_commit, Keypairs
from twccli.twcc.session import Session2
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.services.compute import GpuSite, VcsSite, VcsSecurityGroup, getSecGroupList
from prompt_toolkit.shortcuts import yes_no_dialog


def del_bucket(ids_or_names, is_recursive, isForce=False):
    """Delete bucket

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param is_recursive: is recursive or not
    :type is_recursive: bool
    :param isForce: Force to delete any resources at your own cost.
    :type isForce: bool
    """
    txt = "!! Recursive is ON !!\n"*3 if is_recursive else ""
    if getConfirm("COS Delete Buckets", ",".join(ids_or_names), isForce, ext_txt=txt):
        s3 = S3()
        for bucket_name in ids_or_names:
            s3.del_bucket(bucket_name, is_recursive)
            print("Bucket name '{}' is deleted".format(bucket_name))


def del_object(ids_or_names, bucket_name, isForce=False):
    """Delete Objects by bucket name

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param bucket_name: bucket name
    :type bucket_name: string
    :param isForce: Force to delete any resources at your own cost.
    :type isForce: bool
    """
    txt = "Deleting objects in bucket name: {}".format(bucket_name)
    if getConfirm("COS Delete Buckets", ",".join(ids_or_names), isForce, ext_txt=txt):
        for obj_key in ids_or_names:
            S3().del_object(bucket_name=bucket_name, file_name=obj_key)
            print("Deleted bject name: {}.".format(obj_key))


def del_vcs(ids_or_names, isForce=False):
    if getConfirm("VCS", ",".join(ids_or_names), isForce):
        vsite = VcsSite()
        if len(ids_or_names) > 0:
            for ele in ids_or_names:
                vsite.delete(ele)
                print("VCS resources {} deleted.".format(ele))


def getConfirm(res_name, entity_name, isForce, ext_txt=""):
    """Popup confirm dialog for double confirming to make sure if user really want to delete or not

    :param res_name: name for deleting object.
    :type res_name: string
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    :param ext_txt: extra text
    :type ext_txt: string
    """
    if isForce:
        return isForce
    import sys
    str_title = u'Confirm delete {}:[{}]'.format(res_name, entity_name)
    str_text = u"NOTICE: This action will not be reversible! \nAre you sure?\n{}".format(
        ext_txt)
    # if py3
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
        return yes_no_dialog(title=str_title, text=str_text)
    else:
        return yes_no_dialog(title=str_title, text=str_text).run()


def del_ccs(ids_or_names, isForce=False):
    """Delete ccs by id or name

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    """
    if getConfirm(u"Delete CCS", ", ".join(ids_or_names), isForce):
        ccs = GpuSite()
        for con_id in ids_or_names:
            ans = ccs.delete(con_id)
            print("Successfully remove {}".format(con_id))
    else:
        print("No delete operations.")


def del_keypair(ids_or_names, isForce=False):
    """Delete keypair by name

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    """
    if getConfirm("Keypair", ", ".join(ids_or_names), isForce):
        keyring = Keypairs()
        for key_name in ids_or_names:
            if 'name' in keyring.queryById(key_name):
                print("Keypair: {} deleted.".format(key_name))
                keyring.delete(key_name)
            else:
                raise ValueError("Keypair: {}, not found.".format(key_name))


def del_secg(ids_or_names, isForce=False, isAll=False):
    """Delete security group by site id

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param is_recursive: Recursively delete all objects in COS. NOTE: Use this with caution.
    :type is_recursive: bool
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    :param isAll: Operates as tenant admin
    :type isAll: bool
    """
    secg_id = ids_or_names[0]
    if len(secg_id) <= 6:
        raise ValueError(
            "Security Group id: {} need to longer than 6 characters".format(secg_id))

    vcs = VcsSite()
    sites = vcs.list(isAll)
    secg = VcsSecurityGroup()
    found = []
    for ele in sites:
        secg_list = getSecGroupList(ele['id'])
        for rule in secg_list['security_group_rules']:
            if re.search(secg_id, rule['id']):
                if getConfirm("Security Group", ",".join(ids_or_names), isForce,
                              ext_txt="Resource id: {}\nSecurity Group Rule id: {}".format(ele['id'], rule['id'])):
                    secg.deleteRule(rule['id'])

# Create groups for command
@click.group(help="Delete your TWCC resources.")
def cli():
    pass


@click.command(help="Remove your key in VCS ")
@click.option('-f / --nof', '--force / --noforce', 'force',
              is_flag=True, show_default=True,
              help='Force to delete any resource at your own cost.')
@click.option('-n', '--name', 'name', default=None, type=str,
              help="Enter name for your resource name")
@click.argument('ids_or_names', nargs=-1)
@click.pass_context
def key(ctx, name, ids_or_names, force):
    """Removing key operation

    :param name: Enter name for your resource name
    :type name: string
    :param ids_or_names: Enter ids or names
    :type ids_or_names: string
    :param force: Force to delete any resource at your own cost.
    :type force: bool
    """
    ids_or_names = mk_names(name, ids_or_names)

    if len(ids_or_names) > 0:
        del_keypair(ids_or_names, force)
        wfn = "{}/{}.pem".format(Session2._getTwccDataPath(), name)
        if isFile(wfn):
            print("Please `rm {}` by yourself!".format(wfn))
    else:
        print("Key name is required.")


@click.command(help="'Delete' Operations for VCS (Virtual Compute Service) resources.")
@click.option('-f / --nof', '--force / --noforce', 'force',
              is_flag=True, show_default=True,
              help='Force to delete any resource at your own cost.')
@click.option('-n', '--name', 'name',
              help='Name of the keypair, hash ID of the security group, or ID of the instance.')
@click.option('-all', '--show-all', 'is_all', is_flag=True, type=bool,
              help="Operates as tenant admin.")
@click.option('-key', '--keypair', 'res_property', flag_value='Keypair',
              help="Delete existing keypair(s).")
@click.option('-secg', '--security-group', 'res_property', flag_value='SecurityGroup',
              help="Delete existing security group(s).")
@click.argument('ids_or_names', nargs=-1)
def vcs(res_property, name, force, is_all, ids_or_names):
    """Command line for VCS removing
        Function :
        1. Keypair
        2. Security Group

        :param res_property: Function type (Keypair, SecurityGroup)
        :type res_property: string
        :param name: Key name, security group hash id, or VCS resource id.
        :type name: string
        :param name: Key name, security group hash id, or VCS resource id.
        :type name: string
        :param is_recursive: Recursively delete all objects in COS. NOTE: Use this with caution.
        :type is_recursive: bool
        :param force: Force to delete any resources at your own cost.
        :type force: bool
        :param is_all: Operates as tenant admin.
        :type is_all: bool
    """

    if res_property == "SecurityGroup":
        del_secg(ids_or_names, force, is_all)

    if isNone(res_property):
        if len(ids_or_names) > 0:
            del_vcs(ids_or_names, force)
        else:
            print("Key name is required.")


@click.command(help="'Delete' Operations for COS (Cloud Object Service) resources.")
@click.option('-f / --nof', '--force / --noforce', 'force',
              is_flag=True, show_default=True,
              help='Force delete the objects.')
@click.option('-r', '--recursively', 'is_recursive',
              is_flag=True, show_default=True, default=False,
              help='Recursively delete all objects in the bucket. NOTE: Use with caution.')
@click.option('-bkt', '--bucket-name', 'name',
              help='Name of the bucket.')
@click.argument('ids_or_names', nargs=-1)
def cos(name, force, ids_or_names, is_recursive):
    """Command Line for COS deleting buckets

    :param name: Bucket name for deleting object.
    :type name: string
    :param is_recursive: Recursively delete all objects in COS. NOTE: Use this with caution.
    :type is_recursive: bool
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    :param force: ids_or_names
    :type force: string or tuple
    """
    if not len(ids_or_names) > 0:
        print('please enter bucket_name')
    if isNone(name):
        del_bucket(name, is_recursive, force)
    else:
        del_object(ids_or_names, name, force)


@click.command(help="'Delete' Operations for CCS (Container Compute Service) resources.")
@click.option('-f / --nof', '--force / --noforce', 'force',
              is_flag=True, show_default=True,
              help='Force delete the container.')
@click.option('-s', '--site-id', 'site_id',
              help='ID of the container.')
@click.argument('ids_or_names', nargs=-1)
def ccs(site_id, force, ids_or_names):
    ids_or_names = mk_names(site_id, ids_or_names)
    if len(ids_or_names) == 0:
        raise ValueError("Resource id is required.")
    del_ccs(ids_or_names, force)


cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)
cli.add_command(key)


def main():
    cli()


if __name__ == "__main__":
    main()
