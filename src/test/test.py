#from __future__ import print_function
from twcc.services.base import acls, users, keypairs, projects, api_key
from twcc.services.jobs import jobs
from twcc.services.storage import images, volumes, snapshots, buckets
from twcc.services.solutions import solutions
from twcc.services.compute import sites
from twcc.util import pp, isNone, table_layout

##  7fe2bdd8-be01-430f-865f-feaec9dba27b
csite = 'k8s-taichung-default'
project_id = "898"
mdebug = False

def chk_api_key(key_tokens):
    import json

    table_info = []
    table_cap = ['usr_tag', 'pro', 'acls', 'api_k']
    infos = []
    getTxt = lambda x, y: x['message'][:y] if 'message' in x.keys() else x['detail'][:y]
    better = lambda x: getTxt(x, 20) if len(x) == 1 else len(x)
    for usr in key_tokens:
        a = projects(usr, debug=False)
        a._csite_ = csite
        info = {}
        info['usr_tag'] = usr
        info['pro'] = a.list()
        info['acls'] = acls(usr).list()['total']
        info['api_k'] = api_key(usr).list()['total']
        infos.append(info)

    table_layout(" List api_token ", infos, table_cap, debug=mdebug)


def show_wanted_solution():
    a = projects(user_tag, debug=mdebug)
    a._csite_ = csite
    wanted = set([160, 373, 376, 400, 406, 457])
    a = sites(user_tag, debug=mdebug)
    a.ext_get = {'project': project_id}
    site_list = a.list()

    table_cap = ['id', 'solution', 'status', 'status_reason']
    table_layout(" Results for 'Wanted Sites' ",
        [ a.queryById(x['id']) for x in site_list if x['solution'] in wanted],
        table_cap, debug=mdebug)



def get_solution_for_container(usr, proj_id):
    a = solutions(usr, debug=mdebug)
    print(a.list())
    a.ext_get = {'project': proj_id}
    sol_id = [x['id'] for x in a.list() if x['category']=='container']

    sol_res = []
    sol_cap = []
    for x in sol_id:
        ans = a.queryById(x)
        if len(sol_cap)==0:
            sol_cap = list(ans.keys())
        sol_res.append(ans)

    table_layout(" List only cate: 'container' ", sol_res, sol_cap, debug=mdebug)

def list_site(site_id):
    a = sites(user_tag, debug=mdebug)
    a.ext_get = {'project': project_id}
    ans=a.queryById(site_id)
    ans_cap = list(ans.keys())
    table_layout(" Details of Site: '%s' "%(ans['id']), [ans], ans_cap[:5], debug=mdebug)
    table_layout(" Details of Site: '%s' "%(ans['id']), [ans], ans_cap[5:], debug=mdebug)
    return ans

def get_sol_w_proj(sol_id, pro_id):
    a = projects('sys', debug=True) # usr1 fail
    a._csite_ = 'k8s-taichung-default'
    a.url_dic = {'projects': pro_id, 'solutions':sol_id}
    ans=a.list()['site_extra_prop']
    if len(ans) > 0:
        table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))

def list_cntrs(isFull=True):
    mdebug = True
    b = sites(user_tag, mdebug)
    b._project_id = '2014'
    b._csite_ = 'k8s-taichung-default'

    ans=b.list()
    print(ans)
    if len(ans)==0:
        return None
    for ele in ans:
        #if ele['status'] == 'Error':
        #    print("del Error", ele['id'])
        #    b.delete(ele['id'])

        table_layout(" site_extra_prop for '%s' "%ele['id'], [ele], list(ele.keys()))

        if not isFull:
            continue

        res = b.getDetail(ele['id'])
        for pod in res['Pod']:
            cap = list(pod.keys())
            cap.remove("container")
            table_layout(" > Site Detail [Pod] for '%s' "%ele['id'], [pod], cap)
            for cntr in pod['container']:
                table_layout(" >> container Info. ", [cntr], list(cntr.keys()) )
        for rep in res['ReplicationController']:
            table_layout(" > ReplicationController for '%s' "%ele['id'], [rep], list(rep.keys()))

        if 'Service' in res.keys():
            print ("==="*10)
            for rep in res['Service']:
                table_layout(" > Service for '%s' "%ele['id'], [rep], list(rep.keys()))
            print ("==="*10)

def is_cntr_ready(site_id):
    b = sites(user_tag, mdebug)
    b.project_id = proj_id

def bind_cntr(site_id, port):
    b = sites(user_tag, mdebug)
    b.project_id = proj_id

    pod_name = b.getPodName(site_id)
    bindIp = b.getIpBindAttr([{"inner": 22, "exposed":port}], pod_name) # port must numeric
    b.exposedPort(site_id, bindIp)

def del_cntr(site_id):
    b = sites(user_tag, mdebug)
    b.project_id = proj_id

    b.unbindPort(site_id)
    b.delete(site_id)

def create_cntr():
    mdebug = True
    b = sites(user_tag, mdebug)
    #b.project_id = proj_id
    b._project_id = '2014'

    res = b.create("willtestcon", sol_id, b.getGpuDefaultHeader())
    print(res)
    return res['id']

proj_id = "2014"
sol_id = "865"
user_tag = 'sys'
csite = 'k8s-taichung-default'
mdebug = False

get_sol_w_proj(sol_id, proj_id)
get_solution_for_container(user_tag, proj_id)

if __name__ == "__main__":
    #list_cntrs(isFull=True)
    #create_cntr()
    print(">>>>"*10)
    list_cntrs(isFull=True)

    #import time
    #isBind = False
    #while True:
    #    res = list_site(site_id)
    #    if res['status'] == 'Ready' and not isBind:
    #        bind_cntr(site_id, site_id)
    #        isBind = True
    #    if isBind:
    #        list_cntrs()
    #    time.sleep(5)
    #    print ("\n\n\n")
    del_cntr('5314')


#a = func('sysa', debug=True)
#a._csite_ = 'k8s-taichung-default'
#for func in [images]:
#    a = func('sysa', debug=True)
#    a._csite_ = 'k8s-taichung-default'
#    pp(list=a.list())
#a = keypairs('usr1', debug=False)
#pp(list=a.list())
#pp(list=a.queryById("edbe47e8-093d-48a3-bcf8-3d63163a4b84"))
