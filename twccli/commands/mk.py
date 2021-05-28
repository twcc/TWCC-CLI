# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import click
import time
import sys
from datetime import datetime
from twccli.twcc.services.compute import GpuSite as Sites
from twccli.twcc.services.compute import VcsSite, VcsSecurityGroup, VcsImage, Volumes, LoadBalancers, getServerId
from twccli.twcc.services.solutions import solutions
from twccli.twcc import GupSiteBlockSet
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.util import pp, table_layout, SpinCursor, isNone, jpp, mk_names, isFile, name_validator, timezone2local, window_password_validater
from twccli.twcc.services.base import acls, users, image_commit, Keypairs
from twccli.twcc import GupSiteBlockSet, Session2
from twccli.twcc.services.network import Networks
from twccli.twcc.services.compute_util import doSiteStable, create_vcs
from twccli.twcc.services.generic import GenericService
from twccli.twccli import pass_environment, logger


def create_commit(site_id, tag, isAll=False):
    ccs = Sites()

    site = ccs.getDetail(site_id)
    if 'Pod' in site:
        img_name = site['Pod'][0]['container'][0]['image'].split(
            '/')[-1].split(":")[0]
        c = image_commit()
        return c.createCommit(site_id, tag, img_name)


def create_load_balance(vlb_name, pools, vnet_id, listeners, vlb_desc, is_table, wait):
    """Create load balance by name

    :param vlb_name: Enter Load Balancer name
    :type vlb_name: string
    """
    if not name_validator(vlb_name):
        raise ValueError(
            "Name '{0}' is not valid. '^[a-z][a-z-_0-9]{{5,15}}$' only.".format(vlb_name))
    vlb = LoadBalancers()
    allvlb = vlb.list()
    if [thisvlb for thisvlb in allvlb if thisvlb['name'] == vlb_name]:
        raise ValueError(
            "Name '{0}' is duplicate.".format(vlb_name))
    ans = vlb.create(vlb_name, pools, vnet_id, listeners, vlb_desc)
    if 'detail' in ans:
        is_table = False
    else:
        if wait:
            doSiteStable(ans['id'], site_type='vlb')
            ans = vlb.list(ans['id'])
    if is_table:
        cols = ['id', 'name',  'create_time', 'status']
        table_layout("Load Balancer", ans, cols, isPrint=True)
    else:
        jpp(ans)


def create_volume(vol_name, size, dtype, is_table):
    """Create volume by name

    :param vol_name: Enter volume name
    :type vol_name: string
    """
    if not name_validator(vol_name):
        raise ValueError(
            "Name '{0}' is not valid. '^[a-z][a-z-_0-9]{{5,15}}$' only.".format(vol_name))
    vol = Volumes()
    ans = vol.create(vol_name, size, desc="CLI create Disk", volume_type=dtype.lower())
    if is_table:
        cols = ["id", "name", "size", "volume_type"]
        table_layout("Volumes", ans, cols, isPrint=True)
    else:
        jpp(ans)


def create_bucket(bucket_name):
    """Create bucket by name

    :param bucket_name: Enter bucket name
    :type bucket_name: string
    """
    if not name_validator(bucket_name):
        raise ValueError(
            "Name '{0}' is not valid. '^[a-z][a-z-_0-9]{{5,15}}$' only.".format(bucket_name))
    s3 = S3()
    s3.create_bucket(bucket_name)


def create_cntr(cntr_name, gpu, sol_name, sol_img):
    """Create container
       Create container by default value
       Create container by set vaule of name, solution name, gpu number, solution number

    :param cntr_name: Enter container name
    :type cntr_name: string
    :param sol_img: Enter solution image
    :type sol_img: string
    """
    def_header = Sites.getGpuDefaultHeader(gpu)
    a = solutions()
    cntrs = dict([(cntr['name'], cntr['id']) for cntr in a.list()
                  if not cntr['id'] in GupSiteBlockSet and cntr['name'] == sol_name])
    if len(cntrs) > 0:
        sol_id = cntrs[sol_name]
    else:
        raise ValueError(
            "Solution name '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    b = Sites(debug=False)
    imgs = b.getAvblImg(sol_id, sol_name, latest_first=True)

    if type(sol_img) == type(None) or len(sol_name) == 0:
        def_header['x-extra-property-image'] = imgs[0]
    else:
        if sol_img in imgs:
            def_header['x-extra-property-image'] = sol_img
        else:
            raise ValueError(
                "Container image '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    if not name_validator(cntr_name):
        raise ValueError(
            "Name '{0}' is not valid. ^[a-z][a-z-_0-9]{{5,15}}$ only.".format(cntr_name))
    res = b.create(cntr_name, sol_id, def_header)
    if 'id' not in res.keys():
        if 'message' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['message']))
        if 'detail' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['detail']))
    else:
        return res

# end original function ==================================================


# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="Create (allocate) your TWCC resources.")
def cli():
    try:
        ga = GenericService()
        func_call = '_'.join([i for i in sys.argv[1:] if re.findall(
            r'\d', i) == [] and not i == '-sv']).replace('-', '')
        ga._send_ga(func_call)
    except Exception as e:
        logger.warning(e)
    pass


@click.command(context_settings=dict(max_content_width=500),
               help="Create your VCS (Virtual Compute Service) instances.")
@click.option('-n', '--name', 'name', default=["twccli"], type=str, multiple=True,
              help="Name of the instance.")
@click.option('-s', '--site-id', 'site_id', type=str,
              help="ID of the instance.")
@click.option('-fip', '--need-floating-ip', 'fip',
              is_flag=True, default=False,  flag_value=True,
              help='Assign a floating IP to the instance.')
@click.option('-img', '--img_name', 'img_name', default=None, type=str,
              help="Name of the image.")
@click.option('-key', '--keypair', 'keypair',
              help="Name of the key pair for access your instance.")
@click.option('-net', '--network', 'network', default=None, type=str,
              help="Name of the network.")
@click.option('-pwd', '--password', 'password', default=None, type=str,
              help="Password of the win images.")
@click.option('-envk', '--env_key', 'env_keys',  show_default=False, multiple=True,
              help="The keys of the environment parameters of instances.")
@click.option('-envv', '--env_val', 'env_values',  show_default=False, multiple=True,
              help="The values of the environment parameters of instances.")
@click.option('-itype', '--image-type-name', 'sol', default="Ubuntu", type=str,
              help="Name of the image type.")
@click.option('-ptype', '--product-type', 'flavor', default="v.super", type=str,
              show_default=True,
              help="The product types (hardware configuration).")
@click.option('-cus-img', '--custom-image', 'snapshot', is_flag=True,
              default=False,
              help="Create a custom image for an instance. `-s` is required!")
@click.option('-sys-vol', '--system-volume-type', 'sys_vol', default="HDD", type=str,
              show_default=True,
              help="Disk type of the BOOTABLE disk.")
@click.option('-dd-type', '--data-disk-type', 'data_vol', default="HDD", type=str,
              show_default=True,
              help="Disk type of the DATA disk.")
@click.option('-dd-size', '--data-disk-size', 'data_vol_size', type=int,
              default=0, show_default=True,
              help="Size of the data disk in (GB).")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-wait', '--wait-ready', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your instance to be provisioned.')
@click.argument('ids_or_names', nargs=-1)
@pass_environment
@click.pass_context
def vcs(ctx, env, keypair, name, ids_or_names, site_id, sys_vol,
        data_vol, data_vol_size,
        flavor, img_name, wait, network, snapshot, sol, fip, password, env_keys, env_values, is_table):
    """Command line for create VCS

    :param keypair: Delete existing keypair(s)
    :type keypair: string
    :param name: Enter name for your resources
    :type name: string
    :param sys_vol: Chose system volume disk type
    :type sys_vol: string
    :param data_vol: Volume type of the data volume.
    :type data_vol: int
    :param data_vol_size: Size of the data volume in (GB).
    :type data_vol_size: int
    :type flavor: string
    :param img_name: Enter image name.Enter image name
    :type img_name: string
    :param wait: Wait until resources are provisioned
    :type wait: bool
    :param snapshot: create snapshot list for some VCS
    :type snapshot: bool
    :param network: Enter network name
    :type network: string
    :param sol: Enter TWCC solution name
    :type sol: string
    :param pwd: Password of the win images
    :type pwd: string
    :param fip: Set this flag for applying a floating IP
    :type fip: bool
    :param is_table: Set this flag table view or json view
    :type is_table: bool
    :param ids_or_names: Enter ids or names
    :type ids_or_names: string or tuple
    """

    if snapshot:
        sids = mk_names(site_id, ids_or_names)
        if len(name) == 1 and name[0] == 'twccli':
            pass
        else:
            if not len(name) == len(sids):
                raise ValueError('the number of name should equals to sites')
        created_snap_list = []
        if not isNone(sids) or len(sids) > 0:
            for index, sid in enumerate(sids):
                img_name = ''
                img = VcsImage()
                desc_str = "twccli created at {}".format(
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                if len(name) == 1 and name[0] == 'twccli':
                    img_name = 'twccli'+datetime.now().strftime("%d%m%H%M")+str(index)
                else:
                    img_name = name[index]
                ans = img.createSnapshot(sid, img_name, desc_str)
                if "detail" in ans:
                    is_table = False
                else:
                    img = VcsImage()
                    srv_id = getServerId(sid)
                    searched_imgs = img.list(srv_id)
                    ans = [
                        eachimg for eachimg in searched_imgs if eachimg['name'] == img_name][0]
                created_snap_list.append(ans)
                time.sleep(1)
        ans = created_snap_list
        table_layout_title = "Snapshot Result"

    else:
        if len(name) >= 1:
            name = name[0]
        if name == 'twccli':
            name = "{}{}".format(name, flavor.replace(".", ''))
            if not isNone(password):
                if window_password_validater(password):
                    name = name+'win'
        env_dict = {}
        if not env_keys == None:
            env_keys = list(set(env_keys))
        if not env_keys == None and not env_values == None:
            if len(env_keys) == len(env_values):
                for key,val in zip(env_keys,env_values):
                    env_dict.update({key:val})
            else:
                raise ValueError("env_keys and env_values length is different")
        ans = create_vcs(name, sol=sol.lower(), img_name=img_name,
                         network=network, keypair=keypair,
                         flavor=flavor, sys_vol=sys_vol,
                         data_vol=data_vol.lower(), data_vol_size=data_vol_size,
                         fip=fip, password=password, env = env_dict,)
        ans["solution"] = sol
        ans["flavor"] = flavor

        if wait:
            doSiteStable(ans['id'], site_type='vcs')
            vcs = VcsSite()
            ans = vcs.queryById(ans['id'])
            ans["solution"] = sol
            ans["flavor"] = flavor
        table_layout_title = "VCS Site"
    if is_table:
        cols = ["id", "name", "status"]
        table_layout(table_layout_title, ans, cols, isPrint=True)
    else:
        jpp(ans)


@click.option('-bkt', '--bucket_name', 'name', default="twccli", type=str,
              help="Name of the bucket.")
@click.command(help="Create your COS (Cloud Object Storage) buckets.")
@pass_environment
def cos(env, name):
    """Command line for create cos

    :param name: Enter name for your resources.
    :type name: string
    """
    create_bucket(name)


@click.command(help="Create your key pairs.")
@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of your instance.")
@pass_environment
def key(env, name):
    """Command line for create key

    :param name: Enter name for your resources.
    :type name: string
    """
    keyring = Keypairs()

    if 'name' in keyring.queryById(name):
        raise ValueError("Duplicated name for keypair")

    wfn = "{}/{}.pem".format(Session2._getTwccDataPath(), name)
    if isFile(wfn):
        print("Keypairs exists in {}".format(wfn))
    else:
        ans = keyring.createKeyPair(name)
        with open(wfn, "wb") as fp:
            fp.write(ans)
        import os
        os.chmod(wfn, 0o600)
        print("Your keypair is in `{}` with mode 600".format(wfn))


# end object ===============================================================


@click.command(help="‘Create’ your CCS (Container Computer Service) containers.")
@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of the container.")
@click.option('-s', '--site-id', 'siteId', type=int,
              default=None,
              help='The source container ID to create the duplicate from.')
@click.option('-dup', '--request-duplication', 'req_dup',
              default=False, is_flag=True,
              help='Request duplicating a container.')
@click.option('-gpu', '--gpu-number', 'gpu', default='1', type=str,
              help="Required number of GPU.")
@click.option('-img', '--image-name', 'img_name', default=None, type=str,
              help="Name of the image.")
@click.option('-itype', '--image-type-name', 'sol', default="TensorFlow", type=str,
              help="Name of the image type.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-tag', '--duplication-tag', 'dup_tag',
              default=None,
              help='Create a tag to the duplicate.')
@click.option('-wait', '--wait-ready', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your container to be provisioned.')
@pass_environment
def ccs(env, name, gpu, sol, img_name, wait, req_dup, siteId, dup_tag, is_table):
    """Command line for create ccs

    :param name: Enter name for your resources.
    :type name: string
    :param gpu: Enter desire number for GPU.
    :type gpu: integer
    :param sol: Enter TWCC solution name.
    :type sol: string
    :param img_name: Enter image name. Please check through `twccli ls t cos -img`
    :type img_name: string
    :param wait: Wait until resources are provisioned.
    :type wait: bool
    """
    if req_dup:
        if isNone(siteId):
            raise ValueError("`-s` is required for duplication")
        if isNone(dup_tag):
            dup_tag = "twccli_{}".format(
                datetime.now().strftime("_%m%d%H%M"))
        create_commit(siteId, dup_tag)
    else:
        ans = create_cntr(name, gpu, sol, img_name)
        if wait:
            doSiteStable(ans['id'])
            b = Sites(debug=False)
            ans = b.queryById(ans['id'])
        if is_table:
            cols = ["id", "name", "status"]
            table_layout("CCS Site:{}".format(
                ans['id']), ans, cols, isPrint=True)
        else:
            jpp(ans)


@click.option('-n', '--vnet_name', 'name', default="twccli", type=str,
              help="Name of the virtual network.")
@click.option('-gw', '--getway', 'getway',  type=str,
              help="Virtual Network Getway")
@click.option('-cidr', '--cidr', 'cidr',  type=str,
              help="Classless Inter-Domain Routing")
@click.option('-wait', '--wait-ready', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your virtual network to be builded.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Create your Virtual Network.")
@pass_environment
def vnet(env, name, getway, cidr, is_table, wait):
    """Command line for create virtual network

    :param name: Enter name for your resources.
    :type name: string
    """
    net = Networks()
    # TODO varify getway and cidr @Leo
    import re
    if not re.findall('^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', getway):
        raise ValueError("Getway format error")
    if not '/' in cidr:
        raise ValueError("CIDR format error")
    if not re.findall('^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', cidr.split('/')[0]):
        raise ValueError("CIDR format error")
    ans = net.create(name, getway, cidr)
    if wait:
        doSiteStable(ans['id'], site_type='vnet')
        ans = net.queryById(ans['id'])
    if 'detail' in ans:
        is_table = False
    if is_table:
        cols = ["id", "name", "cidr", "status"]
        table_layout("VCS Networks", ans, cols, isPrint=True)
    else:
        jpp(ans)


@click.option('-n', '--disk-name', 'name', default="twccli", type=str,
              help="Name of the disk.")
@click.option('-t', '--disk-type', default="HDD", type=str, show_default=True,
              help="Disk type: SSD or HDD")
@click.option('-sz', '--disk-size', default=100, type=int, show_default=True,
              help="Size of the disk.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Create your VDS (Virtual Disk Service).")
def vds(name, disk_type, disk_size, is_table):
    """Command line for create vds

    :param name: Enter name for your resources.
    :type name: string
    :param disk_size: Enter size for your resources.
    :type disk_size: int
    :param disk_size: Enter size for your resources.
    :type disk_size: int
    """
    if name=="twccli":
        name="twccli%s%s"%(disk_size, disk_type.lower())
    create_volume(name, disk_size, disk_type, is_table)


@click.option('-d', '--load_balance_description', 'vlb_desc', default="", show_default=True, type=str,
              help="Description of the load balance.")
@click.option('-n', '--load_balance_name', 'vlb_name', default="twccli_lb", type=str,
              help="Name of the load balance.")
@click.option('-lm', '--lb_method', 'lb_methods', required=True, default=["ROUND_ROBIN"], type=click.Choice(['SOURCE_IP', 'LEAST_CONNECTIONS', 'ROUND_ROBIN'], case_sensitive=False), multiple=True,
              help="Method of the load balancer.")
@click.option('-lt', '--listener_type', 'listener_types',   default=["APP_LB"], show_default=True, type=click.Choice(['APP_LB', 'NETWORK_LB'], case_sensitive=False), multiple=True,
              help="The type of the listener of balancer.")
@click.option('-lp', '--listener_port', 'listener_ports',  default=["80"], show_default=True, multiple=True,
              help="The port of the listener of balancer.")
@click.option('-vnn', '--virtual_network_name', 'vnet_name', default="default_network", show_default=True, required=True, type=str,
              help="Virtual Network id")
@click.option('-wait', '--wait-ready', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your container to be provisioned.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Create your Load Balancer.")
def vlb(vlb_name, vnet_name, lb_methods, listener_types, listener_ports, vlb_desc, is_table, wait):
    """Command line for create load balancer

    :param vlb_name: Enter name for your load balancer.
    :type vlb_name: string
    :param vnet_name: Enter virtual network name for your load balancer.
    :type vnet_name: string
    :param lb_methods: Enter mehtod for your load balancer.
    :type lb_methods: string
    :param listener_types: Enter listener type for your load balancer.
    :type listener_types: string
    :param listener_ports: Enter listener port for your load balancer.
    :type listener_ports: string
    :param vlb_desc: Enter descript for your load balancer.
    :type vlb_desc: string
    :param wait: Wait until resources are provisioned.
    :type wait: bool

    """
    if not len(listener_ports) == len(listener_types):
        raise ValueError('the number of listener setting is not correct')
    net = Networks()
    nets = net.list()
    net_name2id = {}
    [net_name2id.setdefault(net['name'], net['id']) for net in nets]
    if not vnet_name in net_name2id:
        raise ValueError('the virtual network name not exist')

    listeners = []
    listener_index = 0
    listener_types_mapping = {'APP_LB': 'HTTP', 'NETWORK_LB': 'TCP'}
    protocol = ''
    for listener_type, listener_port in zip(listener_types, listener_ports):
        listeners.append({'protocol': listener_types_mapping[listener_type], 'protocol_port': listener_port,
                         'name': "listener-{}".format(listener_index), 'pool_name': "pool-0"})
        listener_index += 1
    pools = []
    if len(lb_methods) > 1:
        raise ValueError('not support yet')
    for i, lb_method in enumerate(lb_methods):
        pools.append({'method': lb_method, 'protocol': "HTTP",
                     'name': "pool-{}".format(i)})
    create_load_balance(
        vlb_name, pools, net_name2id[vnet_name], listeners, vlb_desc, is_table, wait)


cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)
cli.add_command(key)
cli.add_command(vds)
cli.add_command(vnet)
cli.add_command(vlb)


def main():
    cli()


if __name__ == "__main__":
    main()
