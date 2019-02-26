from __future__ import print_function
import sys, os
TWCC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path[1]=TWCC_PATH

from termcolor import colored
def TWCC_LOGO():
    print (
        colored(">"*10+" Welcome to ", 'yellow'),
        colored('TWCC.ai', 'white', attrs=['reverse', 'blink']),
        colored(" "+"<"*10, 'yellow')
    )
TWCC_LOGO() ## here is logo
import re
from twcc.util import pp, table_layout, SpinCursor
from twcc.services.solutions import solutions
from twcc.services.base import acls, users
from twcc.services.projects import projects
from twcc.session import session_start
from twcc.services.compute import sites
import click,os
import time

def list_projects():
    proj = projects()
    for cluster in proj.getSites():
        proj._csite_ = cluster
        print ("="*5, cluster, "="*5)
        table_layout ("Proj for {0}".format(cluster), proj.list(), ['id', 'name'])


def list_img(sol_name):
    b = sites(debug=False)
    print(b.getAvblImg(sol_name))

@click.command()
def list_all_img():
    sol_list = sites.getSolList(name_only=True)
    for sol in sol_list:
        list_img(sol)

@click.command()
def list_s3():
    b = sites()
    print(b.getAvblS3())


def doSiteReady(site_id):
    b = sites(debug=False)
    wait_ready = False
    while not wait_ready:
        print("Waiting for container to be Ready.")
        if b.isReady(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id

@click.command()
@click.option('-cntr', 'cntr_name', default = "twcc-cli", type = str, help = "Enter containr name")
@click.option('-gpu', default = 1, type = int, help = "Enter number of gpu")
@click.option('-sol', 'sol_name', default = "Tensorflow", type = str, help = "Enter solution name")
@click.option('-img', 'sol_img', default = None, type = str, help = "Enter image name")
@click.option('-s3','s3', default = [], multiple = True, help = "Enter S3 bucket")
@click.option('-wait', 'isWait', default = True, type = bool,  help = "Need to wait for cntr")
def create_cntr(cntr_name, gpu, sol_name, sol_img, s3,isWait):
    s3 = list(s3)
    def_header = sites.getGpuDefaultHeader(gpu)
    sol_id = sites.checkSolName(sol_name)

    b = sites(debug=False)
    imgs = b.getAvblImg(sol_name, latest_first=True)
    if type(sol_img) == type(None) or len(sol_name)==0:
        def_header['x-extra-property-image'] = imgs[0]
    else:
        if sol_img in imgs:
            def_header['x-extra-property-image'] = sol_img
        else:
            raise ValueError("Container image '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    ## checking S3
    max_mount_s3 = 4
    if len(s3) > max_mount_s3:
        raise ValueError("Mounting S3 buckets are > {0}.".format(max_mount_s3))
    else:
        my_s3_dict = b.getAvblS3(mtype='dict')
        my_s3 = set([ x for x in my_s3_dict])
        mount_s3 = set(s3)

        diff_s3 = mount_s3.difference(my_s3)
        if len(diff_s3) > 0:
            raise ValueError("S3 bucket can NOT mount: {0}.".format( ", ".join(diff_s3) ))
        else:
            def_header['x-extra-property-bucket'] = sites.mkS3MountFormat(s3)


    res = b.create(cntr_name, sol_id, def_header)
    print("Site id: {0} is created.".format(res['id']))

    if isWait:
        doSiteReady(res['id'])
    return int(res['id'])


def list_all_solutions():
    a = solutions()
    cntrs = a.list()
    col_name = ['id','name', 'create_time', 'status', 'status_reason']
    table_layout("all avalible solutions", cntrs, caption_row=col_name)

@click.command()
def list_sol():
    print(sites.getSolList(mtype='list', name_only=True))

def del_all():
    a = sites()
    [ a.delete(site_info['id']) for site_info in a.list()]

def get_all_info():
    a = sites()
    return [ site_info  for site_info in a.list(isAll=True)]

def get_site_detail(site_id):
    a = sites()
    return a.getDetail(site_id)

@click.command()
@click.argument('con_ids', nargs=-1)
def del_cntr(con_ids):
    a = sites()
    if type(con_ids) == type(1):
        con_ids = [con_ids]
    if len(list(con_ids)) > 0:
        for con_id in con_ids:
            a.delete(con_id)
            print("Successfully remove {}".format(con_id))
    else:
        print("Need to enter Container ID")

def gen_cntr(s_id):
    print("This is container information for connection. ")
    b = sites()
    site_id = s_id
    conn_info = b.getConnInfo(site_id)
    print (conn_info)

@click.command()
@click.option('-site', 'site_id', default = 0, type = int, help="Enter the site id")
@click.option('-table', 'isTable', default = True, type = bool, help="Enter the site id")
def list_cntr(site_id, isTable):
    if not type(site_id)==type(1):
        raise ValueError("Site number: '{0}' error.".format(site_id))

    if not isTable:
        gen_cntr(site_id)
    else:
        a = sites()
        if site_id==0:
            my_sites = a.list()
            if len(my_sites)>0:
                col_name = ['id','name', 'create_time', 'status']
                table_layout('sites', my_sites, caption_row=col_name)
        else:
            res = a.queryById(site_id)
            col_name = ['id','name', 'create_time', 'status', 'status_reason']
            table_layout('sites: %s'%site_id, res, caption_row=col_name)

# cli start from here

@click.group()
def cli():
    pass

cli.add_command(list_s3)
cli.add_command(list_sol)
cli.add_command(list_all_img)
cli.add_command(create_cntr)
cli.add_command(list_cntr)
cli.add_command(del_cntr)

if __name__ == "__main__":

    #list_s3()
    #list_sol()
    #list_all_img()

    # min call
    #site_id = create_cntr('twcc-cli-gpu1', 1)
    cli()
    #create_cntr(1, "CNTK", "cntk-18.08-py3-v1:latest", ['05-focusgroup', 'demo112', 'dnntest', 'do-not-delete', 'dwwe1'] )
    #create_cntr('test', 1, "CNTK", "cntk-18.08-py3-v1:latest", ['05-focusgroup', 'demo112', 'dnntest', 'do-not-delete', 'dwwe'] )

    #create_cntr('twcc-cli-test', 1, "Tensorflow", s3=['05-focusgroup', 'demo112', 'dnntest', 'do-not-delete'] )
    # max call, only can mount 4 s3 buckects
    #site_id = create_cntr('twcc-cli-test', 1, "CNTK", "cntk-18.08-py3-v1:latest", ['05-focusgroup', 'demo112', 'dnntest', 'do-not-delete'], True )

    #list_cntr()
    #list_cntr(site_id)
    #list_cntr(site_id, isTable=False)
    #del_cntr(site_id)
    #list_cntr()
