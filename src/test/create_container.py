from __future__ import print_function, unicode_literals
from termcolor import colored
def TWCC_LOGO():
    print (
        colored(">"*10+" Welcome to ", 'yellow'),
        colored('TWCC', 'white', attrs=['reverse', 'blink']),
        colored(" "+"<"*10, 'yellow')
    )
TWCC_LOGO() ## here is logo
import regex
from PyInquirer import prompt, print_json
from PyInquirer import style_from_dict, Token
from PyInquirer import Validator, ValidationError
from twcc.util import pp, table_layout, SpinCursor

from twcc.services.base import acls
from twcc.services.projects import projects
from twcc.session import session_start
from twcc.services.compute import sites
import time

def list_projects():
    proj = projects()
    for cluster in proj.getSites():
        proj._csite_ = cluster
        print ("="*5, cluster, "="*5)
        table_layout ("Proj for {0}".format(cluster), proj.list(), ['id', 'name'])

def create_cntr():
    b = sites()
    sol_id = "865"
    b._project_id = '2299'
    res = b.create("aug_1205", sol_id, b.getGpuDefaultHeader())
    site_id = res['id']

    # wailt for ready
    wait_ready = False
    spin = SpinCursor(msg="Wait for GPU container...", minspin=60, maxspin=600, speed=5)
    spin.start()
    while not wait_ready:
        if b.isReady(site_id):
            wait_ready = True
        time.sleep(5)
    spin.stop()
    print ("\n")
    pod_name = b.getPodName(site_id)
    bindIp = b.getIpBindAttr([
        {"inner": 22, "exposed":site_id},
        {"inner": 8888, "exposed":site_id+1}
        ], pod_name) # port must numeric
    b.exposedPort(site_id, bindIp)

    # show site info
    res = b.getDetail(site_id)
    for pod in res['Pod']:
        cap = list(pod.keys())
        cap.remove("container")
        table_layout(" > Site Detail [Pod] for '%s' "%site_id, [pod], cap)
        for cntr in pod['container']:
            table_layout(" >> container Info. ", [cntr], list(cntr.keys()) )
    for rep in res['ReplicationController']:
        table_layout(" > ReplicationController for '%s' "%site_id, [rep], list(rep.keys()))
    if 'Service' in res.keys():
        for rep in res['Service']:
            table_layout(" > Service for '%s' "%site_id, [rep], list(rep.keys()))

def list_solutions():
    a = sites()
    a._project_id = '2299'
    a.list_solution('865')

def list_cntrs():
    a = sites()
    a._project_id = '2299'
    my_sites = a.list()
    if len(my_sites)>0:
        table_layout('sites', my_sites)

def del_all():
    a = sites()
    a._project_id = '2299'
    [ a.delete(site_info['id']) for site_info in a.list()]

if __name__ == "__main__":
    #list_projects()
    #list_solutions()
    create_cntr()
    #list_cntrs()
    del_all()
