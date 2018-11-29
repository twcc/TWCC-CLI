from twcc.services.network import networks
from twcc.services.base import acls, users, keypairs, projects, api_key, wallet
from twcc.util import pp, isNone, table_layout
from twcc.services.compute import sites



proj_id = "2269"
csite = 'openstack-taichung-community'
def chk_api_key(key_tag):
    b = users(key_tag)
    table_layout(" User Detail:", b.getInfo())
    a = projects(key_tag, debug=False)
    a._csite_ = csite
    proj=a.list()
    print( "Projects: %s"%", ".join([ "%s(%s)"%(x['name'], x['id']) for x in proj] ))

def list_network(key_tag):
    a = networks(key_tag)
    a._project_id = proj_id
    table_layout ("Networks", a.list())

def get_wallet(key_tag):
    a = wallet(key)
    table_layout("My Wallet",  a.list())


def create_cntr(key_tag):
    b = sites(key_tag, False)
    sol_id = "865"
    b.res_type='txt'
    res = b.create("aug_1130", sol_id, b.getGpuDefaultHeader())
    print res

def create_network(key, idx=10):
    b = networks(key)
    b.data_dic = { "name":"badaug_%s"%idx,
                   "project": proj_id,
                   "cidr": "172.18.%s.128/29"%idx,
                   "gateway": "172.18.%s.129"%idx,
                   "with_router": 'true'}
    print(b.create())

if __name__=='__main__':
    key = "littledd-2"
    chk_api_key(key)
    list_network(key)
    #[create_network(key, idx) for idx in range(10)]
    get_wallet(key)
    create_cntr(key)
