from twccli.twcc.services.compute import VcsSite, getServerId, VcsServer
from twccli.twcc.util import pp, jpp, table_layout, SpinCursor, isNone, mk_names

def list_vcs(ids_or_names, is_table, is_all=False, is_print=True):
    vcs = VcsSite()
    ans = []

    if len(ids_or_names) > 0:
        cols = ['id', 'name', 'public_ip', 'private_ip',
                'private_network', 'create_time', 'status']
        if len(ids_or_names) == 1:
            site_id = ids_or_names[0]
            ans = [vcs.queryById(site_id)]
            srvid = getServerId(site_id)
            if isNone(srvid):
                return None
            srv = VcsServer().queryById(srvid)
            if len(srv) > 0 and len(srv[u'private_nets']) > 0:
                srv_net = srv[u'private_nets'][0]
                ans[0]['private_network'] = srv_net[u'name']
                ans[0]['private_ip'] = srv_net[u'ip']
            else:
                ans[0]['private_network'] = ""
                ans[0]['private_ip'] = ""
    else:
        cols = ['id', 'name', 'public_ip', 'create_time', 'status']
        ans = vcs.list(is_all)
    if len(ans) > 0:
        if not is_print:
            return ans

        if is_table:
            table_layout("VCS VMs" if not len(ids_or_names) == 1 else "VCS Info.: {}".format(
                site_id), ans, cols, isPrint=True)
        else:
            jpp(ans)


def list_vcs_img(sol_name, is_table):
    ans = VcsSite.getAvblImg(sol_name)
    if is_table:
        table_layout("Abvl. VCS images", ans, [
                     "product-type", "image"], isPrint=True, isWrap=False)
    else:
        jpp(ans)
