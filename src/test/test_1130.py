from twcc.services.network import networks
from twcc.services.base import acls, users, keypairs, projects, api_key, wallet
from twcc.util import pp, isNone, table_layout
from twcc.services.compute import sites
from twcc.services.solutions import solutions



proj_id = "2269"
csite = 'openstack-taichung-community'
def get_solution_for_container(usr, proj_id):
    a = solutions(usr, debug=False)

    a.ext_get = {'project': proj_id}
    sol_id = [x['id'] for x in a.list() if x['category']=='container']

    sol_res = []
    sol_cap = []
    for x in sol_id:
        ans = a.queryById(x)
        if len(sol_cap)==0:
            sol_cap = list(ans.keys())
        sol_res.append(ans)

    table_layout(" List only cate: 'container' ", sol_res, sol_cap, debug=False)

#get_solution_for_container('littledd-2', proj_id)

def get_sol_w_proj(sol_id, pro_id):
    a = projects('littledd-2', debug=True) # usr1 fail
    a._csite_ = 'k8s-taichung-default'
    a.url_dic = {'projects': pro_id, 'solutions':sol_id}
    print(a.url_dic)
    pp(ans=a.list())
    return None
    ans=a.list()['site_extra_prop']
    if len(ans) > 0:
        table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))


def chk_api_key(key_tag):
    b = users(key_tag)
    table_layout(" User Detail:", b.getInfo())
    a = projects(key_tag, debug=False)
    tmp = []
    for x in ['openstack-taichung-community', 'k8s-taichung-default']:
        a._csite_ = x
        tmp.extend(a.list())
    print( "Projects: %s"%", ".join([ "%s(%s)"%(x['name'], x['id']) for x in tmp] ))

#chk_api_key("littledd-2")
#get_sol_w_proj('865', '2608')
#raw_input("press")

def list_network(key_tag):
    a = networks(key_tag)
    a._project_id = proj_id
    table_layout ("Networks", a.list())

def get_wallet(key_tag):
    a = wallet(key)
    table_layout("My Wallet",  a.list())


def create_cntr():
    b = sites(True)
    sol_id = "865"
    b.res_type='txt'
    b._project_id = '2299'
    b._csite_ = 'k8s-taichung-default'
    res = b.create("aug_1130", sol_id, b.getGpuDefaultHeader())
    pp( res=res)

def create_network(key, idx=10):
    b = networks(key)
    b.data_dic = { "name":"badaug_%s"%idx,
                   "project": '2608',
                   "cidr": "172.18.%s.128/29"%idx,
                   "gateway": "172.18.%s.129"%idx,
                   "with_router": 'true'}
    print(b.create())

if __name__=='__main__':
    key = "littledd"
    #chk_api_key(key)
    #list_network(key)
    ##[create_network(key, idx) for idx in range(10)]
    #get_wallet(key)
    create_cntr()
