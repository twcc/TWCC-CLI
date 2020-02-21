# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from twcc.util import pp, table_layout, SpinCursor, isNone
from twcc.services.compute import GpuSite as Sites
from twcc import GupSiteBlockSet
from twcc.services.solutions import solutions
from twcc.services.base import acls, users, image_commit
from twcc.services.s3_tools import S3

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

def list_cntr(site_id, isTable, isAll):

    if not type(site_id) == type(1):
        raise ValueError("Site number: '{0}' error.".format(site_id))

    if not isTable:
        gen_cntr(site_id)
    else:
        a = Sites()
        if type(a.list(isAll=isAll)) is dict and 'detail' in a.list(isAll=isAll).keys():
            isAll = False
        if site_id == 0:
            my_sites = a.list(isAll=isAll)
            if len(my_sites) > 0:
                col_name = ['id', 'name', 'create_time', 'status']
                table_layout('sites', my_sites, caption_row=col_name, isPrint=True)
        else:
            res = a.queryById(site_id)
            col_name = ['id', 'name', 'create_time', 'status', 'status_reason']
            table_layout('sites: %s' % site_id, res, caption_row=col_name, isPrint=True)

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
@click.group(help="test")
def cli():
    pass

@click.command(help="abbr for vcs")
@click.pass_context
def v(ctx):
    print(ctx)
    print("list vcs")

# end vcs ================================================== 
@click.option('-name', 'name', default=None, type=str,
            help="Enter name for your resources.")
@click.command(help="abbr for cos")
def o(name):

    if isNone(name):
        list_buckets()
    else:
        list_files(name)

# end object ================================================== 

@click.option('-img', 'res_property', flag_value='image')
@click.option('-commit', 'res_property', flag_value='commit')
@click.option('-site',  'site_id', default=0, type=int, help="Enter the site id")
@click.option('-table', 'is_table', default=True, type=bool, help="Show cntr info in table style.")
@click.option('-all',   'is_all', is_flag=True, type=bool, help="Show all container.")
@click.command(help="abbr for cntr")
@click.pass_context
def c(ctx, res_property, site_id, is_table, is_all):
    if res_property == 'image':
        print('image')
        list_all_img()
    
    if res_property == 'commit':
        list_commit()

    if not res_property:
        list_cntr(site_id, is_table, is_all)

# end cntr ====================================================        

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
