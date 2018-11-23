
from twcc.services.base import acls, users, keypairs, projects, api_key
from twcc.services.solutions import solutions
from twcc.util import pp, isNone, table_layout

proj_id = "697"
sol_id = "160"
user_tag = 'sys'
csite = 'k8s-taichung-default'
mdebug = True

def get_sol_w_proj(sol_id):
    a = projects(user_tag, debug=False) # littledd-2 fail
    a._csite_ = 'k8s-taichung-default'
    a.url_dic = {'projects': proj_id, 'solutions':sol_id}
    ans=a.list()['site_extra_prop']
    if len(ans) > 0:
        table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))

def download_sol(sid):
    a = solutions(user_tag, debug=mdebug)
    ans=a.download(sid)
    dest = '/tmp/'
    with open(dest+ans['filename'], 'wb') as f:
        f.write(ans['content'])

def create_sol(name):
    a = solutions(user_tag, debug=mdebug)
    res = a.create("aug_spec", "/tmp/solution_for_aug.gsp")
    print (res)
    #sol_id = "613"
    #a.upload_file(sol_id, "/tmp/solution_for_aug.gsp")

def list_sol():
    a = solutions(user_tag, debug=mdebug)
    ans = a.list()
    table_layout(" Solution for %s "%sol_id, ans, list(ans[0].keys()))

def get_sol(sol_id):
    a = solutions(user_tag, debug=mdebug)
    ans = a.queryById(sol_id)
    table_layout(" Solution for %s "%sol_id, [ans], list(ans.keys()))
    return ans

def make_sol_public(sol_id):
    a = solutions(user_tag, debug=mdebug)
    a.setPublic(sol_id)


if __name__ == "__main__":
    #get_sol_w_proj(sol_id)
    #download_sol(sol_id)
    create_sol('sol_4_aug_t4')

    #get_sol("613")
    #create_sol('')
    list_sol()
    #make_sol_public("643")
