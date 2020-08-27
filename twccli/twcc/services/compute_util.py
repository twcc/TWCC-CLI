import time
from twccli.twcc.services.compute import GpuSite as Sites
from twccli.twcc.services.compute import VcsSite, getServerId, VcsServer
from twccli.twcc.util import pp, jpp, table_layout, SpinCursor, isNone, mk_names, name_validator
from prompt_toolkit.shortcuts import yes_no_dialog

def getConfirm(res_name, entity_name, isForce, ext_txt=""):
    """Popup confirm dialog for double confirming to make sure if user really want to delete or not

    :param res_name: name for deleting object.
    :type res_name: string
    :param force: Force to delete any resources at your own cost.
    :type force: bool
    :param ext_txt: extra text
    :type ext_txt: string
    """
    if isForce:
        return isForce
    import sys
    str_title = u'Confirm delete {}:[{}]'.format(res_name, entity_name)
    str_text = u"NOTICE: This action will not be reversible! \nAre you sure?\n{}".format(
        ext_txt)
    # if py3
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 7):
        return yes_no_dialog(title=str_title, text=str_text)
    else:
        return yes_no_dialog(title=str_title, text=str_text).run()


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
            if not isNone(srvid):
                srv = VcsServer().queryById(srvid)
                if len(srv) > 0 and (u'private_nets' in srv and len(srv[u'private_nets']) > 0):
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

def create_vcs(name, sol=None, img_name=None, network=None,
               keypair="", flavor=None, sys_vol=None,
               data_vol=None, data_vol_size=0, fip=None):
    """Create vcs
    create vcs by set solution, image name, flavor
    create vcs by default value

    :param sys_vol: Chose system volume disk type
    :type sys_vol: string
    :param data_vol: Volume type of the data volume.
    :type data_vol: int
    :param data_vol_size: Size of the data volume in (GB).
    :type data_vol_size: int
    :param flavor: Choose hardware configuration
    :type flavor: string
    :param img_name: Enter image name.Enter image name
    :type img_name: string
    :param network: Enter network name
    :type network: string
    :param sol: Enter TWCC solution name
    :type sol: string
    :param fip: Set this flag for applying a floating IP
    :type fip: bool
    :param name: Enter name
    :type name: string
    """

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

    extra_props = vcs.getExtraProp(exists_sol[sol])

    # x-extra-property-image
    if isNone(img_name):
        img_name = extra_props['x-extra-property-image'][0]
    required['x-extra-property-image'] = img_name

    # x-extra-property-private-network
    if isNone(network):
        network = 'default_network'
    required['x-extra-property-private-network'] = network

    # x-extra-property-keypair
    if isNone(keypair):
        raise ValueError("Missing parameter: `-key`.")
    if not keypair in set(extra_props['x-extra-property-keypair']):
        raise ValueError("keypair: {} is not validated. Avbl: {}".format(keypair,
                                                                         ", ".join(extra_props['x-extra-property-keypair'])))
    required['x-extra-property-keypair'] = keypair

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
        if not data_vol in extra_props['x-extra-property-volume-type'].keys():
            raise ValueError("Data Vlume Type: {} is not validated. Avbl: {}".format(data_vol,
                                                                            ", ".join(extra_props['x-extra-property-volume-type'].keys())))
        required['x-extra-property-volume-type'] = extra_props['x-extra-property-volume-type'][data_vol]

    return vcs.create(name, exists_sol[sol], required)

def del_vcs(ids_or_names, isForce=False):
    """delete a vcs

    :param ids_or_names: name for deleting object.
    :type ids_or_names: string
    :param isForce: Force to delete any resources at your own cost.
    :type isForce: bool
    """
    if getConfirm("VCS", ",".join(ids_or_names), isForce):
        vsite = VcsSite()
        if len(ids_or_names) > 0:
            for ele in ids_or_names:
                vsite.delete(ele)
                print("VCS resources {} deleted.".format(ele))


def doSiteReady(site_id, site_type='cntr'):
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
    else:
        ValueError("Error")

    wait_ready = False
    while not wait_ready:
        if b.isReady(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id
