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
    table_layout("Port info. for {}".format(site_id), b.getConnInfo(site_id), isPrint=True) # todo

def list_commit():
    c = image_commit()
    print(c.getCommitList())


def list_all_img(solution_name):
    print("Note : this operation take 1-2 mins")
    a = solutions()
    if isNone(solution_name) or len(solution_name)==0:
        cntrs = [(cntr['name'], cntr['id']) for cntr in a.list() if not cntr['id'] in GupSiteBlockSet]
    else:
        if len(solution_name)==1:
            solution_name = solution_name[0]
            cntrs = [(cntr['name'], cntr['id']) for cntr in a.list() if not cntr['id'] in GupSiteBlockSet and cntr['name'].lower()==solution_name.lower()]
        
    sol_list = Sites.getSolList(name_only=True)
    base_site = Sites(debug=False)
    output = []
    for (sol_name, sol_id) in cntrs:
        output.append({"sol_name": sol_name,
                       "sol_id": sol_id,
                       "images": base_site.getAvblImg(sol_id, sol_name)})

    table_layout("img", output, ['sol_name', 'sol_id', 'images'], isPrint=True)

def list_cntr(site_ids_or_names, is_table, isAll):
    col_name = ['id', 'name', 'create_time', 'status']
    a = Sites()

    if len(site_ids_or_names) == 0:
        my_sites = a.list(isAll=isAll)
    else:
        my_sites = []
        for ele in site_ids_or_names:
            # site_id = int(ele)
            my_sites.append(a.queryById(ele))
    if len(my_sites) > 0:
        if isAll:
            col_name.append('user')

        if is_table:
            table_layout('sites', my_sites, caption_row=col_name, isPrint=True)
        else:
            return my_sites


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

@click.command(help='Operations for VCS (Virtual Compute Service)')
@click.option('-key', '--keypair', 'res_property', flag_value='Keypair',
                help="List your keypairs in TWCC VCS.")
@click.option('-net', '--network', 'res_property', flag_value='Network',
                help="List existing network in TWCC VCS.")
@click.argument('site_ids_or_names', nargs=-1)
@click.option('--json / --nojson', 'isJson', is_flag=True, default=False,
              help="Show information in JSON view.")
@click.option('-table / -notable','--table-view / --no-table-view', 'is_table', is_flag=True, default=True,
              help="Show information in table view.")
def vcs(res_property, site_ids_or_names, isJson, is_table):
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
        elif is_table:
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
@click.command(help='Operations for COS (Cloud Object Storage)')
@click.option('-name', 'name', default=None, type=str,
            help="Enter name for your resource name")
def cos(name):

    if isNone(name):
        list_buckets()
    else:
        list_files(name)

# end object ==================================================
@click.command(help='Operations for CCS (Container Computer Service)')
@click.option('-img', '--image','res_property', flag_value='image',
             help = 'View all image files. Provid solution name for filtering.')
@click.option('-clone', '--show-clone-status', 'res_property', flag_value='commit',
             help='List the submitted CCS clone requests')
@click.option('-table / -notable', '--table-view / --no-table-view', 'is_table', 
            is_flag=True, default=True, show_default=True,
            help="Show information in Table view.")
@click.option('-json / -nojson', '--json-view / --no-json-view', 'is_json', 
            is_flag=True, default=False, show_default=True,
            help="Show information in JSON view, conflict with -table. @todo")
@click.option('-sol', '--solution-name','res_property', default=None, flag_value='solution',
        help="Show TWCC solutions for CCS.")
@click.option('-all',  '--show-all', 'is_all', is_flag=True, type=bool,
            help="List all the containers in the project. (Tenant Administrators only)")
@click.option('-p', '--port', 'show_ports', is_flag=True,
            help='Show port information.')
@click.argument('ids_or_names', nargs=-1)
def ccs(res_property, ids_or_names, is_table, is_json, is_all, show_ports):
    if res_property == 'image':
        list_all_img(ids_or_names)

    if res_property == 'commit':
        list_commit()

    if res_property == "solution":
        avbl_sols = Sites().getSolList(mtype='list', name_only=True)
        print("Avalible solutions for CCS: {}".format(", ".join(avbl_sols)))

    if not res_property:
        if show_ports:
            if len(ids_or_names)>0:
                for ele in ids_or_names:
                    list_port(ele)
        else:
            list_cntr(ids_or_names, is_table, is_all)

# end cntr ===================================================

cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)



def main():
    cli()


if __name__ == "__main__":
    main()
