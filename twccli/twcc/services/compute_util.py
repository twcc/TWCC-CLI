import re
import click
import time
import json
from twccli.twcc import GupSiteBlockSet
from twccli.twcc.services.compute import GpuSite as Sites
from twccli.twcc.services.compute import VcsSite, getServerId, VcsServer, VcsServerNet, Volumes, LoadBalancers, Fixedip
from twccli.twcc.services.network import Networks
from twccli.twcc.util import jpp, table_layout, isNone, name_validator
from prompt_toolkit.shortcuts import yes_no_dialog
from twccli.twcc.services.solutions import solutions


def getConfirm(res_name, entity_name, is_force, ext_txt=""):
    """Popup confirm dialog for double confirming to make sure if user really want to delete or not

    :param res_name: name for deleting object.
    :type res_name: string
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    :param ext_txt: extra text
    :type ext_txt: string
    """
    if is_force:
        return is_force
    import sys
    str_title = u'Confirm delete {}:[{}]'.format(res_name, entity_name)
    str_text = u"NOTICE: This action will not be reversible! \nAre you sure?\n{}".format(
        ext_txt)
    # if py3
    if sys.version_info[0] >= 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
        return yes_no_dialog(title=str_title, text=str_text)

    import click
    click.echo(click.style(str_title, bg='blue',
                           fg='white', blink=True, bold=True))
    return click.confirm(str_text, default=True)


def list_vcs(ids_or_names, is_table, column='', is_all=False, is_print=True):
    vcs = VcsSite()
    ans = []

    # check if using name
    if len(ids_or_names) == 1 and type("") == type(ids_or_names[0]) and not ids_or_names[0].isnumeric():
        site_name_based = ids_or_names[0]

        # reset input ids_or_names
        ans_ids = vcs.list(is_all)
        ans_ids = [x for x in ans_ids if x['name'] == ids_or_names[0]]
        if len(ans_ids) == 1:
            ids_or_names = [ans_ids[0][u'id']]

    if len(ids_or_names) > 0:
        if column == '':
            cols = ['id', 'name', 'public_ip', 'private_ip',
                    'private_network', 'create_time', 'status']
        else:
            cols = column.split(',')
            if not 'id' in cols:
                cols.append('id')
            if not 'name' in cols:
                cols.append('name')

        for i, site_id in enumerate(ids_or_names):
            site_id = ids_or_names[i]
            ans.extend([vcs.queryById(site_id)])
            srvid = getServerId(site_id)
            if not isNone(srvid):
                srv = VcsServer().queryById(srvid)
                if len(srv) > 0 and (u'private_nets' in srv and len(srv[u'private_nets']) > 0):
                    srv_net = srv[u'private_nets'][0]
                    ans[i]['private_network'] = srv_net[u'name']
                    ans[i]['private_ip'] = srv_net[u'ip']
                else:
                    ans[i]['private_network'] = ""
                    ans[i]['private_ip'] = ""
    else:
        if column == '':
            cols = ['id', 'name', 'public_ip', 'create_time', 'status']
        else:
            cols = column.split(',')
            if not 'id' in cols:
                cols.append('id')
            if not 'name' in cols:
                cols.append('name')
        ans = vcs.list(is_all)

    for each_vcs in ans:
        if each_vcs['status'] == "NotReady":
            each_vcs['status'] = "Stopped"
        if each_vcs['status'] == "Shelving":
            each_vcs['status'] = "Stopping"
        if each_vcs['status'] == "Unshelving":
            each_vcs['status'] = "Starting"
    ans = sorted(ans, key=lambda k: k['create_time'])
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
                     "image-type", "image"], isPrint=True, isWrap=False)
    else:
        jpp(ans)


def create_vcs(name, sol=None, img_name=None, network=None,
               keypair="", flavor=None, sys_vol=None,
               data_vol=None, data_vol_size=0, fip=None, password=None, env=None, pass_api=None):

    vcs = VcsSite()
    exists_sol = vcs.getSolList(mtype='dict', reverse=True)

    if isNone(sol):
        raise ValueError("Please provide solution name. ie:{}".format(
            ", ".join(exists_sol.keys())))
    if not sol.lower() in exists_sol.keys():
        raise ValueError(
            "Solution name: {} not found or not given.".format(sol))

    required = {}
    # check for all param
    if isNone(name):
        raise ValueError("Missing parameter: `-n`.")

    if not name_validator(name):
        raise ValueError(
            "Name '{0}' is not valid. ^[a-z][a-z-_0-9]{{5,15}}$ only.".format(name))

    extra_props = vcs.getExtraProp(exists_sol[sol.lower()])

    # x-extra-property-image
    if isNone(img_name):
        # img_name = "Ubuntu 20.04"
        img_name = sorted(
            extra_props['x-extra-property-image'], reverse=True)[0]
    required['x-extra-property-image'] = img_name
    if not isNone(password):
        required['x-extra-property-password'] = password
    if isNone(network):
        network = 'default_network'
    required['x-extra-property-private-network'] = network

    if isNone(password):
        # x-extra-property-keypair
        if isNone(keypair):
            raise ValueError("Missing parameter: `-key`.")
        if not keypair in set(extra_props['x-extra-property-keypair']):
            raise ValueError("keypair: {} is not validated. Avbl: {}".format(keypair,
                                                                             ", ".join(extra_props['x-extra-property-keypair'])))
        required['x-extra-property-keypair'] = keypair

        get_pass_api_key_params(pass_api, env)

        if not (env == {} or env == None):
            required['x-extra-property-env'] = json.dumps(env)
        else:
            required['x-extra-property-env'] = ""

    # x-extra-property-floating-ip
    required['x-extra-property-floating-ip'] = 'floating' if fip else 'nofloating'

    # x-extra-property-flavor
    if not flavor in extra_props['x-extra-property-flavor'].keys():
        raise ValueError("Flavor: {} is not validated. Avbl: {}".format(flavor,
                                                                        ", ".join(extra_props['x-extra-property-flavor'].keys())))
    required['x-extra-property-flavor'] = extra_props['x-extra-property-flavor'][flavor]

    # x-extra-property-system-volume-type
    sys_vol = sys_vol.lower()
    if not sys_vol in extra_props['x-extra-property-system-volume-type'].keys():
        raise ValueError("System Vlume Type: {} is not validated. Avbl: {}".format(sys_vol,
                                                                                   ", ".join(extra_props['x-extra-property-system-volume-type'].keys())))
    required['x-extra-property-system-volume-type'] = extra_props['x-extra-property-system-volume-type'][sys_vol]

    # x-extra-property-availability-zone
    required['x-extra-property-availability-zone'] = "nova"

    # data vol section
    if data_vol_size > 0:
        required['x-extra-property-volume-size'] = str(data_vol_size)
        if not data_vol in extra_props['x-extra-property-volume-type']:
            raise ValueError("Data Vlume Type: {} is not validated. Avbl: {}".format(data_vol,
                                                                                     ", ".join(extra_props['x-extra-property-volume-type'])))
        required['x-extra-property-volume-type'] = data_vol

    return vcs.create(name, exists_sol[sol], required)


def change_loadbalancer(vlb_id, members, lb_method, is_table):
    # {"pools":[{"name":"pool-0","method":"ROUND_ROBIN","protocol":"HTTP","members":[{"ip":"192.168.1.1","port":80,"weight":1},{"ip":"192.168.1.2","port":90,"weight":1}]}],"listeners":[{"name":"listener-0","pool":6885,"protocol":"HTTP","protocol_port":80,"status":"ACTIVE","pool_name":"pool-0"},{"name":"listener-1","pool":6885,"protocol":"TCP","protocol_port":90,"status":"ACTIVE","pool_name":"pool-0"}]}

    vlb = LoadBalancers()
    vlb_ans = vlb.list(vlb_id)
    member_list = []
    for member in members:
        member_list.append(
            {'ip': member.split(':')[0], 'port': member.split(':')[1], 'weight': 1})
    before_pools = vlb_ans['pools']
    pools_id = before_pools[0]['id']
    pools_name = before_pools[0]['name']
    pools_protocol = before_pools[0]['protocol']
    lb_method = lb_method if not lb_method == None else before_pools[0]['method']
    pools = [{'name': pools_name, 'method': lb_method,
              'protocol': pools_protocol, 'members': member_list}]
    vlb_ans_listeners = vlb_ans['listeners']
    for listener in vlb_ans_listeners:
        listener['pool_name'] = pools_name
        del listener['default_tls_container_ref']
        del listener['sni_container_refs']
    ans = vlb.update(vlb_id, vlb_ans_listeners, pools)
    # for this_ans_pool in ans['pools']:
    #     this_ans['members_IP,status'] = ['({}:{},{})'.format(this_ans_pool_members['ip'],this_ans_pool_members['port'],this_ans_pool_members['status']) for this_ans_pool_members in this_ans_pool['members']]
    # this_ans['listeners_name,protocol,port,status'] = ['{},{},{},{}'.format(this_ans_listeners['name'],this_ans_listeners['protocol'],this_ans_listeners['protocol_port'],this_ans_listeners['status']) for this_ans_listeners in this_ans['listeners']]

    cols = ['id', 'name',  'create_time', 'status', 'vip', 'pools_method',
            'members_IP,status', 'listeners_name,protocol,port,status', 'private_net_name']
    if 'detail' in ans:
        is_table = False
    else:
        ans['private_net_name'] = ans['private_net']['name']
        ans['pools_method'] = ','.join(
            [ans_pool['method'] for ans_pool in ans['pools']])
        for ans_pool in ans['pools']:
            ans['members_IP,status'] = ['({}:{},{})'.format(ans_pool_members['ip'], ans_pool_members['port'],
                                                            ans_pool_members['status']) for ans_pool_members in ans_pool['members']]

        ans['listeners_name,protocol,port,status'] = ['{},{},{},{}'.format(
            ans_listeners['name'], ans_listeners['protocol'], ans_listeners['protocol_port'], ans_listeners['status']) for ans_listeners in ans['listeners']]

    if len(ans) > 0:
        if is_table:
            table_layout("Load Balancers Info.:", ans,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(ans)


def change_volume(ids_or_names, vol_status, site_id, is_table, size, wait, is_print=True):
    if len(ids_or_names) > 0:
        vol = Volumes()
        ans = []
        for vol_id in ids_or_names:
            srvid = getServerId(site_id) if not isNone(site_id) else None
            this_ans = vol.list(vol_id)
            if this_ans['volume_type'] == 'ssd':
                ans.append(
                    {"detail": "Invalid volume: SSD Volume could not to extend"})
                is_table = False
                continue
            this_ans = vol.update(vol_id, vol_status, srvid, size, wait)
            # if detach with wrong site_id, return b'', but with correct site_id, return b'' ...
            if vol_status in ['attach', 'extend'] and 'detail' in this_ans:
                is_table = False
                ans.append(this_ans)
        if not ans:
            for vol_id in ids_or_names:
                ans.append(vol.list(vol_id))
            for the_vol in ans:
                if len(the_vol['mountpoint']) == 1:
                    the_vol['mountpoint'] = the_vol['mountpoint'][0]
    else:
        raise ValueError
    cols = ['id', 'name', 'size', 'create_time',
            'volume_type', 'status', 'mountpoint']
    if len(ans) > 0:
        if is_table:
            table_layout("Volumes" if not len(ids_or_names) == 1 else "Volume Info.: {}".format(
                site_id), ans, cols, isPrint=True)
        else:
            jpp(ans)


def change_ip(ids_or_names, desc, is_table):
    fxip = Fixedip()
    cols = ['id', 'address',  'create_time', 'status', 'type', 'desc']
    if len(ids_or_names) > 0:
        for ip_id in ids_or_names:
            if not isNone(desc):
                ans = fxip.patch_desc(ip_id, desc)
    if len(ans) > 0:
        if is_table:
            table_layout("IP Results",
                         ans,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(ans)


def patch_ccs(ccs, ids_or_names, desc, keep):
    ans = []
    show_col = []
    for i, site_id in enumerate(ids_or_names):
        ans.extend([ccs.queryById(site_id)])
        if not desc == '':
            ccs.patch_desc(site_id, desc)
            show_col.append('desc')
        if not keep == None:
            ccs.patch_keep(site_id, keep)
            show_col.append('termination_protection')
    return ans, show_col


def display_changed_sites(ans, ids_or_names, site, cols, is_print, is_table, titles):
    if len(ans) > 0:
        ans = []
        for i, site_id in enumerate(ids_or_names):
            ans.extend([site.queryById(site_id)])
        if not is_print:
            return ans
        if is_table:
            table_layout(titles[0] if not len(ids_or_names) == 1 else ": {}".format(titles[1],
                                                                                    site_id), ans, cols, isPrint=True)
        else:
            jpp(ans)


def change_ccs(ids_or_names, is_table, desc, keep, is_print=True):
    ccs = Sites()
    ans, show_col = patch_ccs(ccs, ids_or_names, desc, keep)
    if len(ids_or_names) > 0:
        cols = ['id', 'name', 'public_ip', 'create_time', 'status']
        if show_col:
            cols.extend(list(set(show_col)))
    else:
        raise ValueError
    display_changed_sites(ans, ids_or_names, ccs, cols,
                          is_print, is_table, ["GpuSites", "GpuSite Info."])


def vcs_status_mapping(ans):
    for each_vcs in ans:
        if each_vcs['status'] == "NotReady":
            each_vcs['status'] = "Stopped"
        if each_vcs['status'] == "Shelving":
            each_vcs['status'] = "Stopping"
        if each_vcs['status'] == "Unshelving":
            each_vcs['status'] = "Starting"


def action_by_status(status, ans, site_id, srvid, vcs):
    if status == 'stop':
        # Free public IP
        if not isNone(srvid) and re.findall('[0-9.]+', ans['public_ip']):
            VcsServerNet().deAssociateIP(site_id)
        vcs.stop(site_id)
    elif status == 'ready':
        vcs.start(site_id)
    elif status == 'reboot':
        VcsServerNet().reboot(srvid)
    else:
        pass


def do_ch_vcs(ids_or_names, vcs, status, desc, keep):
    ans = []
    if len(ids_or_names) > 0:
        show_col = []
        for i, site_id in enumerate(ids_or_names):
            ans.extend([vcs.queryById(site_id)])
            srvid = getServerId(site_id)
            action_by_status(status, ans[i], site_id, srvid, vcs)
            if not desc == '':
                vcs.patch_desc(site_id, desc)
                show_col.append('desc')
            if not keep == None:
                vcs.patch_keep(site_id, keep)
                show_col.append('termination_protection')
    else:
        raise ValueError
    return ans, show_col


def change_vcs(ids_or_names, status, is_table, desc, keep, wait, is_print=True):
    vcs = VcsSite()
    ans, show_col = do_ch_vcs(ids_or_names, vcs, status, desc, keep)
    cols = ['id', 'name', 'public_ip', 'create_time', 'status']
    if show_col:
        cols.extend(list(set(show_col)))
    if wait and status == 'stop':
        for i, site_id in enumerate(ids_or_names):
            doSiteStopped(site_id)
    if wait and status == 'ready':
        for i, site_id in enumerate(ids_or_names):
            doSiteStable(site_id, site_type='vcs')
    display_changed_sites(ans, ids_or_names, vcs, cols,
                          is_print, is_table, ["VCS VMs", "VCS Info."])


def check_proteced(site_info, vsite, ele):
    if site_info['termination_protection']:
        click.echo(click.style("Delete fail! VCS resources {} is protected.".format(
            ele), bg='red', fg='white', blink=True, bold=True))
    else:
        vsite.delete(ele)
        print("VCS resources {} deleted.".format(ele))


def del_vcs(ids_or_names, is_force=False):
    """delete a vcs

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param is_force: Force to delete any resources at your own cost.
    :type is_force: bool
    """
    if getConfirm("VCS", ",".join(ids_or_names), is_force):
        vsite = VcsSite()
        if len(ids_or_names) > 0:
            for ele in ids_or_names:
                site_info = vsite.queryById(ele)
                if site_info and 'detail' in site_info:
                    click.echo(click.style(
                        site_info['detail'], bg='red', fg='white', bold=True))
                else:
                    check_proteced(site_info, vsite, ele)


def doSiteStopped(site_id):
    b = VcsSite()
    wait_ready = False
    while not wait_ready:
        if b.isStopped(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id


def doSiteStable(site_id, site_type='cntr'):
    """Check if site is created or not

    :param site_id: Enter site id
    :type site_id: string
    :param site_type: Enter site type
    :type site_type: string
    """
    if site_type == 'cntr':
        b = Sites()
    elif site_type == 'vcs':
        b = VcsSite()
    elif site_type == 'vnet':
        b = Networks()
    elif site_type == 'vlb':
        b = LoadBalancers()
    else:
        raise ValueError("Error")

    wait_ready = False
    while not wait_ready:
        if b.isStable(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id


def format_ccs_env_dict(env_dict):
    if not isNone(env_dict) and len(env_dict) > 0:
        return json.dumps([env_dict])
    else:
        return ""


def get_ccs_sol_id(sol_name):
    a = solutions()
    sol_name = sol_name.lower()
    cntrs = dict([(cntr['name'].lower(), cntr['id']) for cntr in a.list()
                  if not cntr['id'] in GupSiteBlockSet and cntr['name'].lower() == sol_name])
    if len(cntrs) > 0:
        return cntrs[sol_name]
    else:
        raise ValueError(
            "Solution name '{0}' is not valid.".format(sol_name))


def get_ccs_img(sol_id, sol_name, sol_img, gpu=1):
    ccs_site = Sites(debug=False)
    imgs = ccs_site.getAvblImg(sol_id, sol_name, latest_first=True)
    if isNone(sol_img) or len(sol_name) == 0:
        return imgs[0]
    else:
        if sol_img in imgs:
            return sol_img
        else:
            raise ValueError(
                "Container image '{0}' for '{1}' is not valid.".format(sol_img, sol_name))


def get_pass_api_key_params(is_apikey, env_dict):
    if not isNone(is_apikey) and is_apikey:
        import click
        import socket
        from twccli.twcc.session import Session2

        sess = Session2()
        env_dict['_TWCC_API_KEY_'] = sess.twcc_api_key
        env_dict['_TWCC_CLI_GA_'] = "1"
        env_dict['_TWCC_PROJECT_CODE_'] = sess.twcc_proj_code
        env_dict['_TWCC_CREDENTIAL_TRANSER_FROM_SITE_'] = socket.gethostname()


def create_ccs(cntr_name, gpu, flavor, sol_name, sol_img, cmd, env_dict, is_apikey):
    """Create container
       Create container by default value
       Create container by set vaule of name, solution name, gpu number, solution number
    """

    get_pass_api_key_params(is_apikey, env_dict)

    def_header = Sites.getGpuDefaultHeader(flavor, sol_name, gpu)
    sol_id = get_ccs_sol_id(sol_name)
    def_header['x-extra-property-image'] = get_ccs_img(
        sol_id, sol_name, sol_img, gpu)
    def_header['x-extra-property-env'] = format_ccs_env_dict(env_dict)
    if not cmd == None:
        def_header['x-extra-property-command'] = cmd
    if not name_validator(cntr_name):
        raise ValueError(
            "Name '{0}' is not valid. ^[a-z][a-z-_0-9]{{5,15}}$ only.".format(cntr_name))

    ccs_site = Sites(debug=False)
    res = ccs_site.create(cntr_name, sol_id, def_header)

    if 'id' not in res.keys():
        if 'message' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['message']))
        if 'detail' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['detail']))
    else:
        return res
