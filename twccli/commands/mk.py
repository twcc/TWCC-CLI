# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import sys
import json
import time
import click
from datetime import datetime
from collections import defaultdict
from twccli.twcc.services.compute import GpuSite as Sites
from twccli.twcc.services.compute import VcsSite, VcsSecurityGroup, VcsImage, Volumes, LoadBalancers, getServerId, Fixedip, Secrets
from twccli.twcc import GupSiteBlockSet
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.util import pp, table_layout, isNone, jpp, mk_names, isFile, name_validator, window_password_validater, _debug
from twccli.twcc.services.base import acls, users, image_commit, Keypairs
from twccli.twcc import Session2
from twccli.twcc.services.network import Networks
from twccli.twcc.services.compute_util import doSiteStable, create_vcs, create_ccs, list_vcs
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


def create_fixedip(desc, is_table):
    """Create volume by name

    :param vol_name: Enter volume name
    :type vol_name: string
    """
    eip = Fixedip()
    ans = eip.create(desc=desc)
    if is_table:
        cols = ["id", "address", "desc", "create_time", "type"]
        table_layout("IPs", ans, cols, isPrint=True)
    else:
        jpp(ans)


def mk_temp_by_vlb_id(json_template, vlb_id):
    if not isNone(vlb_id):
        vlb = LoadBalancers()
        exist_vlb_json = vlb.list(vlb_id)
        json_template["name"] = exist_vlb_json["name"]
        json_template["private_net"] = exist_vlb_json["private_net"]["id"]
        json_template["pools"] = []
        pool_id2name = {}
        for pool in exist_vlb_json["pools"]:
            json_template["pools"].append(
                {"name": pool["name"], "protocol": pool["protocol"], "members": pool["members"], "method": pool["method"]})
            pool_id2name[pool["id"]] = pool["name"]
        json_template["listeners"] = []
        for listener in exist_vlb_json["listeners"]:
            json_template["listeners"].append({"name": listener["name"], "pool_name": pool_id2name[listener["pool"]],
                                              "protocol": listener["protocol"], "protocol_port": listener["protocol_port"]})
    return json_template


def check_vlb_parameter(listener_ports, listener_types, lb_methods, members, json_file):
    json_data = None
    if json_file:
        with open(json_file, 'r') as fn:
            json_data = json.load(fn)
    elif not members == ():
        if not (len(listener_ports) == len(listener_types) == len(lb_methods) == len(members)):
            raise ValueError(
                'the number of listener_ports, listener_types, lb_methods should be the same')
    else:
        if not (len(listener_ports) == len(listener_types) == len(lb_methods)):
            raise ValueError(
                'the number of listener_ports, listener_types should be the same')
    return json_data


def create_load_balance(vlb_name, pools, vnet_id, listeners, vlb_desc, is_table, wait, json_data=None, eip_id=None):
    """Create load balance by name

    :param vlb_name: Enter Load Balancer name
    :type vlb_name: string
    """
    vlb = LoadBalancers()
    allvlb = vlb.list()
    if not isNone(json_data):
        vlb_name = json_data['name']
    if [thisvlb for thisvlb in allvlb if thisvlb['name'] == vlb_name]:
        raise ValueError(
            "Name '{0}' is duplicate.".format(vlb_name))
    ans = vlb.create(vlb_name, pools, vnet_id, listeners,
                     vlb_desc, json_data=json_data, eip_id=eip_id)
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
    ans = vol.create(vol_name, size, desc="CLI create Disk",
                     volume_type=dtype.lower())
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


def get_params_seq(argv_list, argv_key):
    # process seq problems
    argv_envk = defaultdict(str)
    for idx in range(len(argv_list)):
        if argv_list[idx] == argv_key and idx + 1 < len(argv_list):
            argv_envk[idx] = argv_list[idx + 1]
    return argv_envk


def mk_env_dict(arg_envk="-envk", arg_envv="-envv"):
    """
    這個函式是用來處理參數的，可以讓使用者輸入多個參數，並且可以讓使用者輸入多個參數，並且可以讓使用者輸入多個參數。
    因為需要確認參數排序，所以直接使用 sys.argv 去比對處理，從而不處理 -envk -envv 的傳入資料。
    """

    env_keys = get_params_seq(sys.argv, arg_envk).values()
    env_values = get_params_seq(sys.argv, arg_envv).values()

    env_dict = {}
    if not env_keys == None and not env_values == None:
        if len(env_keys) == len(env_values):
            for key, val in zip(env_keys, env_values):
                env_dict.update({key: val})
        else:
            raise ValueError("env_keys and env_values length is different")
    # fix for #344
    env_dict["BUFFER"] = json.dumps(env_dict)
    return env_dict

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


default_vcs_name = 'twcc-vcs_'


@click.command(context_settings=dict(max_content_width=500),
               help="Create your VCS (Virtual Compute Service) instances.")
@click.option('-n', '--name', 'name', default=[default_vcs_name], type=str, multiple=True,
              help="Name of the instance.")
@click.option('-s', '--site-id', 'site_id', type=str,
              help="ID of the instance.")
@click.option('-eip', '--eip', 'eip',
              default=None, type=str,
              help='Assign a EIP to the instance.')
@click.option('-fip', '--need-floating-ip', 'fip',
              is_flag=True, default=False,  flag_value=True,
              help='Assign a floating IP to the instance.')
@click.option('-img', '--image-name', 'img_name', default=None, type=str,
              help="Name of the image.")
@click.option('-key', '--keypair', 'keypair',
              help="Name of the key pair for access your instance.")
@click.option('-net', '--network', 'network', default=None, type=str,
              help="Name of the network.")
@click.option('-pwd', '--password', 'password', default=None, type=str,
              help="Password of the win images.")
@click.option('-envk', '--environment-keys', 'env_keys',  show_default=False, multiple=True,
              help="The keys of the environment parameters of instances.")
@click.option('-envv', '--environment-values', 'env_values',  show_default=False, multiple=True,
              help="The values of the environment parameters of instances.")
@click.option('-itype', '--image-type-name', 'sol', default="Ubuntu", type=str,
              help="Name of the image type.")
@click.option('-ptype', '--product-type', 'flavor', default="v.super", type=str,
              show_default=True,
              help="The product types (hardware configuration).")
@click.option('-apikey / -nokey', '--pass-apikey / --no-pass-apikey', 'is_apikey',
              is_flag=True, default=True, show_default=True,
              help="Transfer TWCC API Key to new environment.")
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
        data_vol, data_vol_size, flavor, img_name, wait, network, snapshot,
        sol, fip, password, env_keys, env_values, eip,  is_apikey, is_table):
    if snapshot:
        sids = mk_names(site_id, ids_or_names)
        if len(name) == 1 and name[0] == default_vcs_name:
            pass
        else:
            if not len(name) == len(sids):
                raise ValueError('the number of name should equals to sites')
        created_snap_list = []
        if not isNone(sids) or len(sids) > 0:
            for index, sid in enumerate(sids):
                img_name = ''

                vms = list_vcs(sids, is_print=False, is_table=False)
                vm_name = [x for x in vms if int(x['id']) == int(sids[0])][0]['name']

                img = VcsImage()
                # time just ignore
                desc_str = "twccli created from {}({})".format(vm_name, sids[0])
                if len(name) == 1 and name[0] == default_vcs_name:
                    img_name = "VCSi-" + vm_name[:8]
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
        table_layout_title = "Build VCSi Result"

    else:
        if len(name) >= 1:
            name = name[0]
        if name == default_vcs_name:
            name = "{}{}".format(name, flavor.replace(".", ''))[:15]
            if not isNone(password):
                if window_password_validater(password):
                    name = name+'win'

        ans = create_vcs(name, sol=sol.lower(), img_name=img_name,
                         network=network, keypair=keypair,
                         flavor=flavor, sys_vol=sys_vol,
                         data_vol=data_vol.lower(), data_vol_size=data_vol_size,
                         fip=fip, password=password, env=mk_env_dict(), pass_api=is_apikey, eip=eip,)
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
        if is_apikey:
            click.echo(click.style("Passing current credential information to new computing resources.",
                       bg='blue', fg='white', blink=False, bold=True))

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
@click.option('-pub', '--public-key', 'public_key', default=None, type=str, help="Public key for your new key.")
@pass_environment
def key(env, name, public_key):
    """Command line for create key

    :param name: Enter name for your resources.
    :type name: string
    """
    keyring = Keypairs()

    wfn = "{}/{}.pem".format(Session2._getTwccDataPath(), name)
    if isFile(wfn):
        print("Keypairs exists in {}".format(wfn))
    else:
        ans = keyring.createKeyPair(name, public_key)
        with open(wfn, "wb") as fp:
            fp.write(ans)
        import os
        os.chmod(wfn, 0o600)
        print("Your keypair is in `{}` with mode 600".format(wfn))


@click.command(help="‘Create’ your CCS (Container Computer Service) containers.")
@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of the container.")
@click.option('-s', '--site-id', 'site_id', type=int,
              default=None,
              help='The source container ID to create the duplicate from.')
@click.option('-dup', '--request-duplication', 'req_dup',
              default=False, is_flag=True,
              help='Request duplicating a container.')
@click.option('-gpu', '--gpu-number', 'gpu', default='1', type=str,
              help="Required number of GPU.")
@click.option('-cmd', '--command', 'cmd', default=None, type=str,
              help="The command for the container.")
@click.option('-img', '--image-name', 'img_name', default=None, type=str,
              help="Name of the image.")
@click.option('-envk', '--environment-keys', 'env_keys',  show_default=False, multiple=True,
              help="The keys of the environment parameters of instances.")
@click.option('-envv', '--environment-values', 'env_values',  show_default=False, multiple=True,
              help="The values of the environment parameters of instances.")
@click.option('-itype', '--image-type-name', 'sol', default="TensorFlow", type=str,
              help="Name of the image type.")
@click.option('-ptype', '--product-type', 'flavor', default=None, type=str,
              help="The product types (hardware configuration).")
@click.option('-apikey / -nokey', '--pass-apikey / --no-pass-apikey', 'is_apikey',
              is_flag=True, default=True, show_default=True,
              help="Transfer TWCC API Key to new environment.")
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
def ccs(env, name, gpu, cmd, flavor, sol, img_name,
        env_keys, env_values, wait, req_dup, site_id, dup_tag, is_apikey, is_table):

    if req_dup:
        if isNone(site_id):
            raise ValueError("`-s` is required for duplication")
        if isNone(dup_tag):
            dup_tag = "twccli_{}".format(
                datetime.now().strftime("_%m%d%H%M"))
        create_commit(site_id, dup_tag)
    else:
        ans = create_ccs(name, gpu, flavor, sol, img_name, cmd,
                         mk_env_dict(), is_apikey)
        if wait:
            doSiteStable(ans['id'])
            b = Sites(debug=False)
            ans = b.queryById(ans['id'])
        if is_table:
            cols = ["id", "name", "status"]

            if is_apikey:
                click.echo(click.style("Passing current credential information to new computing resources.",
                                       bg='blue', fg='white', blink=False, bold=True))

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
    if not re.findall(r"^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$", getway):
        raise ValueError("Getway format error")
    if not '/' in cidr:
        raise ValueError("CIDR format error")
    if not re.findall(r"^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$", cidr.split('/')[0]):
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
    if name == "twccli":
        name = "twccli%s%s" % (disk_size, disk_type.lower())
    create_volume(name, disk_size, disk_type, is_table)


@click.option('-d', '--load_balance_description', 'vlb_desc', default="", show_default=True, type=str,
              help="Description of the load balance.")
@click.option('-n', '--load_balance_name', 'vlb_name', default="twccli_lb", type=str,
              help="Name of the load balance.")
@click.option('-id', '--vlb-id', 'vlb_id', type=int,  default=None,
              help="Index of the volume.")
@click.option('-ip', '--eip', 'eip', type=str,  default=None,
              help="Index of the EIP.")
@click.option('-lm', '--lb_method', 'lb_methods', required=True, default=["ROUND_ROBIN"], type=click.Choice(['SOURCE_IP', 'LEAST_CONNECTIONS', 'ROUND_ROBIN'], case_sensitive=False), multiple=True,
              help="Method of the load balancer.")
@click.option('-lt', '--listener_type', 'listener_types',   default=["APP_LB"], show_default=True, type=click.Choice(['APP_LB', 'NETWORK_LB'], case_sensitive=False), multiple=True,
              help="The type of the listener of balancer.")
@click.option('-lp', '--listener_port', 'listener_ports',  default=["80"], show_default=True, multiple=True,
              help="The port of the listener of balancer.")
@click.option('-ms', '--members', 'members', type=str, multiple=True, default=None,
              help="The members for each listener, using ',' to seperate. ex: 192.168.1.1:80,192.168.1.2:80")
@click.option('-vnn', '--virtual_network_name', 'vnet_name', default="default_network", show_default=True, required=True, type=str,
              help="Virtual Network id")
@click.option('-temp', '--template', 'template',
              is_flag=True, default=False, flag_value=True,
              help='Create template vlb json file.')
@click.option('-wait', '--wait-ready', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your container to be provisioned.')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-byjson', '--byjson', 'json_file', default="", show_default=False, type=str,
              help="Create load balance by json file.")
@click.command(help="Create your Load Balancer.")
def vlb(vlb_id, vlb_name, vnet_name, lb_methods, listener_types, listener_ports, vlb_desc, members, is_table, wait, template, json_file, eip):
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

    eip_id = Fixedip().get_id_by_ip(eip)
    if not isNone(eip) and eip_id is None:
        raise ValueError("EIP not avalible")
    if template:
        json_template = {"name": "TestLBS (required)",
                         "desc": "This LBS is for .... (optional)",
                         "private_net": "The ID of the network on which to allocate the VIP (required)",
                         "pools": [{
                             "name": "TestPool (required)",
                             "protocol": "TCP, HTTP, or HTTPS (required)",
                             "members": [
                                 {
                                     "ip": "string",
                                     "port": 0,
                                     "weight": 0
                                 }
                             ],
                             "method": "ROUND_ROBIN, LEAST_CONNECTIONS, or SOURCE_IP (required)",
                         }
                         ],
                         "listeners": [
                             {
                                 "name": "TestListener (required)",
                                 "pool_name": "TestPool (required)",
                                 "protocol": "TCP, HTTP, HTTPS, or TERMINATED_HTTPS (required)",
                                 "protocol_port": "from 0 to 65535 (required)",
                             }
                         ]
                         }
        json_template = mk_temp_by_vlb_id(json_template, vlb_id)
        with open('vlb_template', 'w') as fn:
            json.dump(json_template, fn)
        click.echo("Create template vlb json file successfully.")
    else:
        json_data = check_vlb_parameter(
            listener_ports, listener_types, lb_methods, members, json_file)

        net = Networks()
        nets = net.list()
        net_name2id = {}
        [net_name2id.setdefault(net['name'], net['id']) for net in nets]
        if not vnet_name in net_name2id:
            raise ValueError('the virtual network name not exist')

        listeners = []
        pools = []
        listener_index = 0
        listener_types_mapping = {'APP_LB': 'HTTP', 'NETWORK_LB': 'TCP'}
        for listener_type, listener_port, lb_method in zip(listener_types, listener_ports, lb_methods):
            listeners.append({'protocol': listener_types_mapping[listener_type], 'protocol_port': listener_port,
                              'name': "listener-{}".format(listener_index), 'pool_name': "pool-{}".format(listener_index)})
            pools.append({'method': lb_method, 'protocol': listener_types_mapping[listener_type],
                          'name': "pool-{}".format(listener_index)})
            listener_index += 1

        create_load_balance(
            vlb_name, pools, net_name2id[vnet_name], listeners, vlb_desc, is_table, wait, json_data=json_data, eip_id=eip_id)


# @click.option('-netid', '--private-net-id', type=int,
#               help="Index of the private-net.")
@click.option('-d', '--IP-description', 'desc', type=str, default='generated by cli',
              help="Description of the private-net.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Create your fixed ips.")
def eip(desc, is_table):
    """Command line for list vds

    :param ip_id: Enter id for your fixed ips.
    :type ip_id: string
    :param ids_or_names: Enter more than one id for your fixed ip.
    :type ids_or_names: string

    """
    create_fixedip(desc, is_table)


@click.command(help="Create your SSL certificates.")
@click.option('-d', '--SSL-description', 'desc', type=str, default='generated by cli',
              help="Description of the SSL certificate.")
@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of your SSL.")
@click.option('-p', '--payload', 'payload', default=None, type=str,
              help="Base64 encoding of your SSL.")
@click.option('-sca', '--sercer-certfile', 'sercer_certfile', default=None, type=str,
              help="Server certfile for your openssl.")
@click.option('-inkey', '--inkey', 'inkey', default=None, type=str,
              help="Server key for your openssl.")
@click.option('-ica', '--intermediate-CA', 'intermediate_ca', default=None, type=str,
              help="Intermediate CA for your openssl.")
@click.option('-pf', '--payload-file', 'payload_file', default=None, type=str,
              help="Base64 file path of your SSL.")
@click.option('-et', '--expire-time', 'expire_time', default=None, type=str,
              help="Expire-time of your SSL.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@pass_environment
def ssl(env, name, desc, payload, payload_file, expire_time, sercer_certfile, inkey, intermediate_ca, is_table):
    """Command line for create SSL

    :param name: Enter name for your resources.
    :type name: string
    """

    if not(isNone(inkey) or isNone(sercer_certfile) or isNone(intermediate_ca)):
        import subprocess
        import os
        command = 'openssl pkcs12 -export -nodes -out server.p12 -inkey {} -in {} -certfile {} -passout pass: ; openssl base64 -in server.p12 -out server.txt'.format(
            inkey, sercer_certfile, intermediate_CA)
        subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT).decode('utf8').strip()
        payload_file = os.path.join(os.getcwd(), 'server.txt')
    ssl = Secrets()
    if not isNone(payload_file):
        with open(payload_file, 'r') as f:
            payload = f.read()
    ans = ssl.create(name, desc, payload, expire_time)
    ans = ssl.list(ans['id'])
    if is_table:
        cols = ["id", "name", "status", "create_time"]
        table_layout("IPs", ans, cols, isPrint=True)
    else:
        jpp(ans)


# end object ===============================================================
cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)
cli.add_command(key)
cli.add_command(vds)
cli.add_command(vnet)
cli.add_command(vlb)
cli.add_command(eip)
cli.add_command(ssl)


def main():
    cli()


if __name__ == "__main__":
    main()
