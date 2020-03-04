# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
from twcc.util import pp, table_layout, SpinCursor, isNone
from twcc.services.compute import GpuSite as Sites
from twcc import GupSiteBlockSet
from twcc.services.solutions import solutions
from twcc.services.base import acls, users, image_commit
from twcc.services.s3_tools import S3
from twcc.services.network import Networks
from twcc.services.base import acls, users, image_commit, Keypairs

def list_port(site_id):
    b = Sites()
    conn_info = b.getConnInfo(site_id)

def list_commit():
    print('list commit')
    c = image_commit()
    print(c.getCommitList())


def list_all_img():
    print("Note : this operation take 1-2 mins")
    a = solutions()
    cntrs = [(cntr['name'], cntr['id'])
             for cntr in a.list() if not cntr['id'] in GupSiteBlockSet]
    sol_list = Sites.getSolList(name_only=True)
    base_site = Sites(debug=False)
    output = []
    for (sol_name, sol_id) in cntrs:
        output.append({"sol_name": sol_name,
                       "sol_id": sol_id,
                       "images": base_site.getAvblImg(sol_id, sol_name)})

    table_layout("img", output, ['sol_name', 'sol_id', 'images'], isPrint=True)

def gen_cntr(s_id):
    print("This is container information for connection. ")
    b = Sites()
    site_id = s_id
    conn_info = b.getConnInfo(site_id)
    print(conn_info)

def list_cntr(site_ids_or_names, isTable, isAll):
    col_name = ['id', 'name', 'create_time', 'status']
    a = Sites()

    if len(site_ids_or_names) == 0:
        my_sites = a.list(isAll=isAll)
    else:
        my_sites = []
        for ele in site_ids_or_names:
            try:
                site_id = int(ele)
                if is_site_id(site_id):
                    my_sites.append(a.queryById(ele))
            except:
                # @todo add query filter
                pass
    if len(my_sites) > 0:
        if isAll:
            col_name.append('user')

        if isTable:
            table_layout('sites', my_sites, caption_row=col_name, isPrint=True)
        else:
            return my_sites
    return []


def list_buckets():
    s3 = S3()
    buckets = s3.list_bucket()
    s3.test_table(buckets)

def list_files(bucket_name):
    s3 = S3()
    files = s3.list_object(bucket_name)
    s3.test_table(files)

# end orginal function ====================================

# Create groups for command
@click.group(help="List Information")
def cli():
    pass

@click.command(help='vcs(Virtual Compute Service)')
@click.option('-key', '--keypair', 'res_property', flag_value='Keypair',
                help="List your keypairs in TWCC VCS.")
@click.option('-net', '--network', 'res_property', flag_value='Network',
                help="List existing network in TWCC VCS.")
@click.argument('site_ids_or_names', nargs=-1)
@click.option('--json / --nojson', 'isJson', is_flag=True, default=False,
              help="Show information in JSON view.")
@click.option('-table / -notable','--table-view / --no-table-view', 'isTable', is_flag=True, default=True,
              help="Show information in table view.")

def v(res_property, site_ids_or_names, isJson, isTable):
    if res_property == 'Network':
        net = Networks()
        if len(site_ids_or_names)>0:
            ans = [ net.queryById(x) for x in site_ids_or_names]
            cols = [ "id", "name", "cidr", "create_time", "gateway", "nameservers", "status", "user"]
        else:
            ans = net.list()
            cols = [ "id", "name", "cidr", "create_time", "status"]

        if isJson:
             print(json.dumps(ans, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
        elif isTable:
            table_layout("VCS Networks", ans, cols, isPrint=True)
        return True

    if res_property == 'Keypair':
        keyring = Keypairs()
        if len(site_ids_or_names)>0:
             ans = []
             cols = ['name', 'fingerprint', 'create_time', 'user']
             for ele in site_ids_or_names:
                 ans.append(keyring.queryById(ele))
        else:
             cols = ['name', 'fingerprint']
             ans = keyring.list()

        table_layout(' Existing Keypairs ', ans, cols, isPrint=True)

# end vcs ==================================================
@click.command(help='cos(Cloud Object Storage)')
@click.option('-name', 'name', default=None, type=str,
            help="Enter name for your resource name")
def o(name):

    if isNone(name):
        list_buckets()
    else:
        list_files(name)

# end object ==================================================
@click.command(help='ccs(Container Computer Service)')
@click.option('-img', '--image','res_property', flag_value='image',
             help = 'View all image files')
@click.option('-clone', '--make-clone', 'res_property', flag_value='commit',
             help='List the submitted requests')
@click.option('--table-view / --no-table-view', 'isTable', is_flag=True, default=True,
            help="Show information in table view.")
@click.option('-all',  '--show-all', 'is_all', is_flag=True, type=bool,
            help="List all the containers in the project (Tenant Administrators only)")
@click.option('--port', 'show_ports', is_flag=True,
            help='Show site port information in table style cntr only')
@click.argument('site_ids_or_names', nargs=-1)
def c(res_property, site_ids_or_names, isTable, is_all, show_ports):
    if res_property == 'image':
        print('image')
        list_all_img()

    if res_property == 'commit':
        list_commit()

    if not res_property:
        if show_ports:
            if len(site_ids_or_names)>0:
                for ele in site_ids_or_names:
                    print(ele)
                    list_port(ele)
        else:
            list_cntr(site_ids_or_names, isTable, is_all)

# end cntr ===================================================

cli.add_command(v)
cli.add_command(o)
cli.add_command(c)



def main():
    cli()


if __name__ == "__main__":
    main()
