from __future__ import print_function
import click
import time
from prompt_toolkit.shortcuts import get_input
from twccli.twcc.services.compute import sites
from twccli.twcc.session import session_start
from twccli.twcc.services.projects import projects
from twccli.twcc.services.base import acls, users, image_commit
from twccli.twcc.services.solutions import solutions
from twccli.twcc.util import pp, table_layout, SpinCursor
from twccli.twcc import GupSiteBlockSet
import re
from termcolor import colored
import sys
import os

TWCC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

sys.path[1] = TWCC_PATH


def TWCC_LOGO():
    print (
        colored(">"*10+" Welcome to ", 'yellow'),
        colored('TWCC.ai', 'white', attrs=['reverse', 'blink']),
        colored(" "+"<"*10, 'yellow')
    )


TWCC_LOGO()  # here is logo


def list_projects():
    proj = projects()
    for cluster in proj.getSites():
        proj._csite_ = cluster
        print ("="*5, cluster, "="*5)
        table_layout("Proj for {0}".format(cluster),
                     proj.list(), ['id', 'name'])


# @click.command()
def list_all_img():
    print("NOTE: This operation will take 1~2 mins.")
    a = solutions()
    cntrs = [(cntr['name'], cntr['id'])
             for cntr in a.list() if not cntr['id'] in GupSiteBlockSet]
    sol_list = sites.getSolList(name_only=True)
    base_site = sites(debug=False)
    output = []
    for (sol_name, sol_id) in cntrs:
        output.append({"sol_name": sol_name,
                       "sol_id": sol_id,
                       "images": base_site.getAvblImg(sol_id, sol_name)})

    table_layout("img", output, ['sol_name', 'sol_id', 'images'])


@click.command()
def list_s3():
    b = sites()
    print(b.getAvblS3())


def doSiteStable(site_id):
    b = sites(debug=False)
    wait_ready = False
    while not wait_ready:
        print("Waiting for container to be Ready.")
        if b.isStable(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id


@click.command()
@click.option('-cntr', 'cntr_name', default="twcc-cli", type=str, help="Enter containr name")
@click.option('-gpu', default=1, type=int, help="Enter number of gpu")
@click.option('-sol', 'sol_name', default="TensorFlow", type=str, help="Enter solution name")
@click.option('-img', 'sol_img', default=None, type=str, help="Enter image name")
# @click.option('-s3','s3', default = [], multiple = True, help = "Enter S3 bucket") # dont use
@click.option('-wait', 'isWait', default=True, type=bool,  help="Need to wait for cntr")
def create_cntr(cntr_name, gpu, sol_name, sol_img, isWait):
    def_header = sites.getGpuDefaultHeader(gpu)

    a = solutions()
    cntrs = dict([(cntr['name'], cntr['id']) for cntr in a.list(
    ) if not cntr['id'] in GupSiteBlockSet and cntr['name'] == sol_name])
    if len(cntrs) > 0:
        sol_id = cntrs[sol_name]
    else:
        raise ValueError(
            "Solution name '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    b = sites(debug=False)
    imgs = b.getAvblImg(sol_id, sol_name, latest_first=True)
    if type(sol_img) == type(None) or len(sol_name) == 0:
        def_header['x-extra-property-image'] = imgs[0]
    else:
        if sol_img in imgs:
            def_header['x-extra-property-image'] = sol_img
        else:
            raise ValueError(
                "Container image '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    res = b.create(cntr_name, sol_id, def_header)
    if 'id' not in res.keys():
        if 'message' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['message']))
        if 'detail' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['detail']))
    else:
        print("Site id: {0} is created.".format(res['id']))

    if isWait:
        doSiteStable(res['id'])
    return int(res['id'])


def list_all_solutions():
    a = solutions()
    cntrs = a.list()
    col_name = ['id', 'name', 'create_time']
    table_layout("all avalible solutions", cntrs, caption_row=col_name)


@click.command()
def list_sol():
    list_all_solutions()
    print(sites.getSolList(mtype='list', name_only=True))


def del_all():
    a = sites()
    [a.delete(site_info['id']) for site_info in a.list()]


def get_all_info():
    a = sites()
    return [site_info for site_info in a.list(isAll=True)]


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
@click.option('-site', 'site_id', default=0, type=int, help="Enter the site id")
@click.option('-table', 'isTable', default=True, type=bool, help="Show cntr info in table style.")
@click.option('-all', 'isAll', is_flag=True, type=bool, help="Show all container.")
def list_cntr(site_id, isTable, isAll):
    if not type(site_id) == type(1):
        raise ValueError("Site number: '{0}' error.".format(site_id))

    if not isTable:
        gen_cntr(site_id)
    else:
        a = sites()
        if type(a.list(isAll=isAll)) is dict and 'detail' in a.list(isAll=isAll).keys():
            isAll = False
        # raise ValueError("{}, please change to Admin key".format(a.list(isAll=isAll)['detail']))
        if site_id == 0:
            my_sites = a.list(isAll=isAll)
            if len(my_sites) > 0:
                col_name = ['id', 'name', 'create_time', 'status']
                table_layout('sites', my_sites, caption_row=col_name)
        else:
            res = a.queryById(site_id)
            col_name = ['id', 'name', 'create_time', 'status', 'status_reason']
            table_layout('sites: %s' % site_id, res, caption_row=col_name)


@click.command()
def list_commit():
    c = image_commit()
    print(c.getCommitList())


@click.command()
def create_commit():
    a = sites()
    isAll = True

    if type(a.list(isAll=isAll)) is dict and 'detail' in a.list(isAll=isAll).keys():
        isAll = False

        my_sites = a.list(isAll=isAll)
        if len(my_sites) > 0:
            col_name = ['id', 'name', 'create_time', 'status']
            table_layout('sites', my_sites, caption_row=col_name)

    site_id = get_input(
        u'Please Input the site ID which you would like to commit: ')
    tag = get_input(u'Please Input the image tag  ')
    image = get_input(u'Please Input the image name: ')
    c = image_commit()
    print(c.createCommit(site_id, tag, image))

# cli start from here


@click.group()
def cli():
    pass


cli.add_command(list_s3)
cli.add_command(list_sol)
# cli.add_command(list_all_img)
cli.add_command(create_cntr)
cli.add_command(list_cntr)
cli.add_command(del_cntr)
cli.add_command(list_commit)
cli.add_command(create_commit)

if __name__ == "__main__":

    cli()
