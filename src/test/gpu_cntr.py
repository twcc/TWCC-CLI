from __future__ import print_function
import sys, os
TWCC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path[1]=TWCC_PATH

from termcolor import colored
def TWCC_LOGO():
    print (
        colored(">"*10+" Welcome to ", 'yellow'),
        colored('TWCC', 'white', attrs=['reverse', 'blink']),
        colored(" "+"<"*10, 'yellow')
    )
TWCC_LOGO() ## here is logo
import re
#from PyInquirer import prompt, print_json
#from PyInquirer import style_from_dict, Token
#from PyInquirer import Validator, ValidationError
from twcc.util import pp, table_layout, SpinCursor
from twcc.services.solutions import solutions
from twcc.services.base import acls, users, wallet
from twcc.services.projects import projects
from twcc.session import session_start
from twcc.services.compute import sites
import click,os
import time

pro_big = "44"
use_sol_id = "4"
_def_proj_ = pro_big

def list_projects():
    proj = projects()
    for cluster in proj.getSites():
        proj._csite_ = cluster
        print ("="*5, cluster, "="*5)
        table_layout ("Proj for {0}".format(cluster), proj.list(), ['id', 'name'])

@click.command()
def create():
    b = sites()
    sol_id = use_sol_id
    b._project_id = _def_proj_
    res = b.create("vtr_working", sol_id, b.getGpuDefaultHeader())
    if 'id' in res:
        site_id = res['id']
    else:
        pp(res=res)
        return False

    wait_ready = False
    while not wait_ready:
        if b.isReady(site_id):
            wait_ready = True
        time.sleep(5)
    print("site_id: %s"%site_id)

def list_all_solutions():
    a = solutions()
    a._project_id = _def_proj_
    table_layout("all avalible solutions", a.list())


@click.command()
def list_sol():
    a = sites()
    a._project_id = _def_proj_
    a.list_solution('4')

@click.command()
def list():
    a = sites()
    a._project_id = _def_proj_
    my_sites = a.list()
    if len(my_sites)>0:
        table_layout('sites', my_sites)

def del_all():
    a = sites()
    a._project_id = _def_proj_
    [ a.delete(site_info['id']) for site_info in a.list()]

@click.command()
@click.argument('con_ids', nargs=-1)
def rm(con_ids):
    a = sites()
    a.proejct_id = _def_proj_
    if len(con_ids) > 0:
        for con_id in con_ids:
            a.delete(con_id)
            print("Successfully remove {}".format(con_id))
    else:
        print("Need to enter Container ID")

@click.command()
@click.argument('s_id',nargs=1)
def gen(s_id):
    print("This is container information for connection. ")
    b = sites()
    site_id = s_id
    conn_info = b.getConnInfo(site_id)
    print (conn_info)

@click.group()
def cli():
    pass

cli.add_command(create)
cli.add_command(list)
cli.add_command(list_sol)
cli.add_command(gen)
cli.add_command(rm)

if __name__ == "__main__":
    cli()
