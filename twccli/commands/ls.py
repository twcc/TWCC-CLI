# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
from twccli.twcc.util import pp, jpp, table_layout, SpinCursor, isNone, mk_names
from twccli.twcc.services.compute import GpuSite, VcsSite, VcsSecurityGroup
from twccli.twcc.services.compute import getServerId, getSecGroupList
from twccli.twcc import GupSiteBlockSet
from twccli.twcc.services.solutions import solutions
from twccli.twcc.services.base import acls, users, image_commit
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.services.network import Networks
from twccli.twcc.services.base import acls, users, image_commit, Keypairs


def list_port(site_id):
    b = GpuSite()
    table_layout("Port info. for {}".format(site_id),
                 b.getConnInfo(site_id, ssh_info=False), isPrint=True)  # todo


def list_commit():
    c = image_commit()
    print(c.getCommitList())


def list_all_img(solution_name):
    print("Note : this operation take 1-2 mins")
    a = solutions()
    if isNone(solution_name) or len(solution_name) == 0:
        cntrs = [(cntr['name'], cntr['id'])
                 for cntr in a.list() if not cntr['id'] in GupSiteBlockSet]
    else:
        if len(solution_name) == 1:
            solution_name = solution_name[0]
            cntrs = [(cntr['name'], cntr['id']) for cntr in a.list() if not cntr['id']
                     in GupSiteBlockSet and cntr['name'].lower() == solution_name.lower()]

    sol_list = GpuSite.getSolList(name_only=True)
    base_site = GpuSite(debug=False)
    output = []
    for (sol_name, sol_id) in cntrs:
        output.append({"sol_name": sol_name,
                       "sol_id": sol_id,
                       "images": base_site.getAvblImg(sol_id, sol_name)})

    table_layout("img", output, ['sol_name', 'sol_id', 'images'], isPrint=True)


def list_cntr(site_ids_or_names, is_table, isAll):
    col_name = ['id', 'name', 'create_time', 'status']
    a = GpuSite()

    if len(site_ids_or_names) == 0:
        my_GpuSite = a.list(isAll=isAll)
    else:
        my_GpuSite = []
        for ele in site_ids_or_names:
            # site_id = int(ele)
            my_GpuSite.append(a.queryById(ele))
    if len(my_GpuSite) > 0:
        if isAll:
            col_name.append('user')

        if is_table:
            table_layout('GpuSite', my_GpuSite,
                         caption_row=col_name, isPrint=True)
        else:
            jpp(my_GpuSite)
    else:
        table_layout('GpuSite', [],
                     caption_row=col_name, isPrint=True)


def list_buckets(is_table):
    s3 = S3()
    buckets = s3.list_bucket()
    if is_table:
        table_layout("COS buckets {}", buckets, isWrap=False, isPrint=True)
    else:
        jpp(buckets)


def list_files(ids_or_names, is_table):
    s3 = S3()
    for bucket_name in ids_or_names:
        files = s3.list_object(bucket_name)

        if is_table and not isNone(files):
            table_layout("COS objects {}".format(
                bucket_name), files, isPrint=True)
        else:
            jpp(files)


def list_secg(name, ids_or_names, isJson=False, isTable=True):
    ids_or_names = mk_names(name, ids_or_names)
    if not len(ids_or_names) > 0:
        raise ValueError("Need resource id for listing security group")

    if len(ids_or_names) == 1:
        secg_list = getSecGroupList(ids_or_names[0])
        secg_id = secg_list['id']
        secg_detail = secg_list['security_group_rules']
        if isJson:
            jpp(secg_detail)
        elif isTable:
            table_layout("SecurityGroup for {}".format(ids_or_names[0]),
                         secg_detail, isPrint=True)
        return True

# end orginal function ====================================

# Create groups for command
@click.group(help="LiSt resources operations.")
def cli():
    pass


@click.command(help='Operations for VCS (Virtual Compute Service)')
@click.option('-key', '--keypair', 'res_property', flag_value='Keypair',
              help="List your keypairs in TWCC VCS. Equals to `ls key`")
@click.option('-net', '--network', 'res_property', flag_value='Network',
              help="List existing network in TWCC VCS.")
@click.option('-secg', '--security-group', 'res_property', flag_value='SecurityGroup',
              help="List existing security groups for VCS instance.")
@click.argument('site_ids_or_names', nargs=-1)
@click.option('-all',  '--show-all', 'is_all', is_flag=True, type=bool,
              help="List all the containers in the project. (Tenant Administrators only)")
@click.option('-n', '--name', 'name', default=None, type=str,
              help="Enter name for your resources.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-sol', '--solution-name', 'res_property', default=None, flag_value='solution',
              help="Show TWCC solutions for VCS.")
@click.option('-img', '--image', 'res_property', flag_value='image',
              help='View all image files. Provid solution name for filtering.')
@click.pass_context
def vcs(ctx, res_property, site_ids_or_names, name, is_table, is_all):
    if isNone(res_property):
        vcs = VcsSite()

        if len(site_ids_or_names) > 0:
            cols = ['id', 'name', 'public_ip', 'create_time', 'user', 'status']
            ans = [vcs.queryById(x) for x in site_ids_or_names]
        else:
            cols = ['id', 'name', 'public_ip', 'create_time', 'status']
            ans = vcs.list(is_all)

        if is_table:
            table_layout("VCS VMs", ans, cols, isPrint=True)
        else:
            jpp(ans)

        return True

    if res_property == 'image':
        list_all_img(site_ids_or_names)

    if res_property == "solution":
        avbl_sols = GpuSite().getSolList(mtype='list', name_only=True)
        print("Avalible solutions for CCS: {}".format(", ".join(avbl_sols)))

    if res_property == 'Network':
        net = Networks()
        if len(site_ids_or_names) > 0:
            ans = [net.queryById(x) for x in site_ids_or_names]
            cols = ["id", "name", "cidr", "create_time",
                    "gateway", "nameservers", "status", "user"]
        else:
            ans = net.list()
            cols = ["id", "name", "cidr", "create_time", "status"]

        if is_table:
            table_layout("VCS Networks", ans, cols, isPrint=True)
        else:
            jpp(ans)

    if res_property == 'SecurityGroup':
        list_secg(name, site_ids_or_names, is_table)

    if res_property == 'Keypair':
        # forward to key()
        ctx.invoke(key, ids_or_names=site_ids_or_names,
                   name=name, is_table=is_table)

    if res_property == 'SecurityGroup':
        list_secg(name, site_ids_or_names, is_table)

    if isNone(res_property):  # add for list vcs, @amber need to work on this
        vcs = VcsSite()

        if len(site_ids_or_names) > 0:
            cols = ['id', 'name', 'public_ip', 'create_time', 'user', 'status']
            ans = [vcs.queryById(x) for x in site_ids_or_names]
        else:
            cols = ['id', 'name', 'public_ip', 'create_time', 'status']
            ans = vcs.list(is_all)

        if is_table:
            table_layout("VCS VMs", ans, cols, isPrint=True)
        else:
            jpp(ans)


# end vcs ==================================================
@click.command(help='Operations for COS (Cloud Object Storage)')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-n', '--name', 'name', default=None, type=str,
              help="Enter name for your resource name")
@click.argument('ids_or_names', nargs=-1)
def cos(name, is_table, ids_or_names):
    ids_or_names = mk_names(name, ids_or_names)
    if len(ids_or_names) == 0:
        list_buckets(is_table)
    else:
        list_files(ids_or_names, is_table)

# end object ==================================================
@click.command(help='Operations for CCS (Container Computer Service)')
@click.option('-img', '--image', 'res_property', flag_value='image',
              help='View all image files. Provid solution name for filtering.')
@click.option('-clone', '--show-clone-status', 'res_property', flag_value='commit',
              help='List the submitted CCS clone requests')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-sol', '--solution-name', 'res_property', default=None, flag_value='solution',
              help="Show TWCC solutions for CCS.")
@click.option('-all',  '--show-all', 'is_all', is_flag=True, type=bool,
              help="List all the containers in the project. (Tenant Administrators only)")
@click.option('-p', '--port', 'show_ports', is_flag=True,
              help='Show port information.')
@click.argument('site_ids_or_names', nargs=-1)
def ccs(res_property, site_ids_or_names, is_table, is_all, show_ports):
    if res_property == 'image':
        list_all_img(site_ids_or_names)

    if res_property == 'commit':
        list_commit()

    if res_property == "solution":
        avbl_sols = GpuSite().getSolList(mtype='list', name_only=True)
        print("Avalible solutions for CCS: {}".format(", ".join(avbl_sols)))

    if not res_property:
        if show_ports:
            if len(site_ids_or_names) > 0:
                for ele in site_ids_or_names:
                    list_port(ele)
            else:
                raise ValueError("Need at least one resource id.")
        else:
            list_cntr(site_ids_or_names, is_table, is_all)


@click.command(help='List your keypairs in VCS.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-n', '--name', 'name', default=None, type=str,
              help="Enter name for your resource name")
@click.argument('ids_or_names', nargs=-1)
@click.pass_context
def key(ctx, name, is_table, ids_or_names):
    ids_or_names = mk_names(name, ids_or_names)

    keyring = Keypairs()
    if len(ids_or_names) > 0:
        ans = []
        cols = ['name', 'fingerprint', 'create_time', 'user']
        for ele in ids_or_names:
            ans.append(keyring.queryById(ele))
    else:
        cols = ['name', 'fingerprint']
        ans = keyring.list()

    if is_table:
        table_layout(' Existing Keypairs ', ans, cols, isPrint=True, isWrap=False)
    else:
        jpp(ans)


cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)
cli.add_command(key)


def main():
    cli()


if __name__ == "__main__":
    main()

