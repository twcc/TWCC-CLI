#from __future__ import print_function
from twcc.services.base import acls, users, keypairs, projects, api_key
from twcc.services.jobs import jobs
from twcc.services.storage import images, volumes, snapshots, buckets
from twcc.services.solutions import solutions
from twcc.services.compute import sites
from twcc.util import pp, isNone, table_layout
from joblib import Parallel, delayed
import dill as pickle
import collections
import time

##  7fe2bdd8-be01-430f-865f-feaec9dba27b
csite = 'k8s-taichung-default'
project_id = "898"
proj_id = "2269"
mdebug = False

def chk_api_key(key_tokens):
    import json

    table_info = []
    table_cap = ['usr_tag', 'pro', 'acls', 'api_k']
    table_cap = ['usr_tag', 'MST107106', 'total projects']
    infos = []
    getTxt = lambda x, y: x['message'][:y] if 'message' in x.keys() else x['detail'][:y]
    better = lambda x: getTxt(x, 20) if len(x) == 1 else len(x)
    for usr in key_tokens:
        a = projects(usr, debug=False)
        a._csite_ = csite
        info = {}
        info['usr_tag'] = usr
        info['MST107106'] = ", ".join([ x['name'] for x in a.list() if x['name']=='MST107106'])
        info['total projects'] = len(a.list())
        #info['acls'] = acls(usr).list()
        #info['api_k'] = api_key(usr).list()
        infos.append(info)

    table_layout(" List api_token ", infos, table_cap, debug=mdebug)

chk_api_key(["littledd-2"])

def show_wanted_solution():
    user_tag = 'littledd-2'
    mdebug=True
    a = projects(user_tag, debug=mdebug)
    a._csite_ = csite
    a._project_id = proj_id
    wanted = set(['865'])
    a = sites(user_tag, debug=mdebug)
    a.ext_get = {'project': proj_id}
    a._project_id = proj_id
    site_list = a.list()
    pp(site_list=site_list)
    #table_cap = ['id', 'solution', 'status', 'status_reason']
    #table_layout(" Results for 'Wanted Sites' ",
    #    [ a.queryById(x['id']) for x in site_list if x['solution'] in wanted],
    #    table_cap, debug=mdebug)

show_wanted_solution()


def get_solution_for_container(usr, roj_id):
    a = solutions(usr, debug=mdebug)

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
    a = projects(user_tag, debug=True) # usr1 fail
    a._csite_ = 'k8s-taichung-default'
    a.url_dic = {'projects': pro_id, 'solutions':sol_id}
    print(a.url_dic)
    pp(ans=a.list())
    return None
    ans=a.list()['site_extra_prop']
    if len(ans) > 0:
        table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))

def list_cntrs(isFull=True):
    mdebug = False
    b = sites('littledd', mdebug)
    b._project_id = proj_id
    b._csite_ = 'k8s-taichung-default'

    ans=b.list()

    if len(ans)==0:
        return None

    for ele in ans:
        #if ele['status'] == 'Error':
        #    print("del Error", ele['id'])
        #    b.delete(ele['id'])

        table_layout(" Site details for '%s' "%ele['id'], [ele], list(ele.keys()))

        if not isFull:
            continue

        pp(res=ele['status'])

        if ele['status'] == 'Error':
            pass
        else:
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
                for rep in res['Service']:
                    table_layout(" > Service for '%s' "%ele['id'], [rep], list(rep.keys()))

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
    print "del: %s"%(site_id)
    b = sites(user_tag, mdebug)
    b.project_id = proj_id

    b.unbindPort(site_id)
    b.delete(site_id)

def create_cntr(idx):
    mdebug = False
    b = sites(user_tag, mdebug)
    #b.project_id = proj_id
    b._project_id = '2608'

    res = b.create("bad_aug_%s"%(idx), sol_id, b.getGpuDefaultHeader())
    site_id = res['id']
    isBind = False
    isStop = False
    cntr = 1
    while not isStop:
        #res = list_site(site_id)
        if res['status'] == 'Ready' and not isBind:
            bind_cntr(site_id, site_id)
            isBind = True
        if isBind and res['public_ip'].split(".")[0]=="203" :
            #list_cntrs(isFull=False)
            isStop = True
        if cntr > 40:
            isStop = True
            print ("site %s: fail to bind port in %s sec."%(site_id, cntr*5))
        cntr += 1
        print ("(%s) bind %s for site_id: %s, current public_ip %s."%(cntr, site_id, site_id, res['public_ip'] if 'public_ip' in res else "not bind"))
        time.sleep(5)

    return site_id

proj_id = "2608"
sol_id = "865"
user_tag = 'littledd'
csite = 'k8s-taichung-default'
mdebug = False

#get_sol_w_proj(sol_id, proj_id)
#get_solution_for_container(user_tag, proj_id)


if __name__ == "__main__":
    #list_cntrs(isFull=False)
    b = sites('littledd', mdebug)
    b._project_id = proj_id
    b._csite_ = 'k8s-taichung-default'

    max_cntr = 2
    job_num = max_cntr if max_cntr < 10 else 20
    ## massive create
    #Parallel(n_jobs=job_num, backend='multiprocessing')(delayed(create_cntr)(idx) for idx in range(max_cntr))

    ## count success
    #err = []
    #b._project_id = '2608'
    #all_created_site = Parallel(n_jobs=job_num, backend='multiprocessing')( delayed(b.queryById)(res['id']) for res in b.list() )
    #for res in all_created_site:
    #    site_stat = b.queryById(res['id'])
    #    if site_stat['status']=='Error':
    #        err.append("%s_%s"%(site_stat['status'], site_stat['status_reason'].split(" ")[0]))
    #    else:
    #        err.append(site_stat['status'])
    #results = collections.Counter(err)
    #for (k,w) in results.most_common(100):
    #    print "%s, %s"%(k, w)



    # massive delete
    #Parallel(n_jobs=job_num, backend='multiprocessing')(delayed(del_cntr)(res['id']) for res in b.list())



#a = func('sysa', debug=True)
#a._csite_ = 'k8s-taichung-default'
#for func in [images]:
#    a = func('sysa', debug=True)
#    a._csite_ = 'k8s-taichung-default'
#    pp(list=a.list())
#a = keypairs('usr1', debug=False)
#pp(list=a.list())
#pp(list=a.queryById("edbe47e8-093d-48a3-bcf8-3d63163a4b84"))
