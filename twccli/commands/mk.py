# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import time
from twcc.services.compute import GpuSite as Sites
from twcc.services.compute import VcsSite, VcsSecurityGroup
from twcc.services.solutions import solutions
from twcc import GupSiteBlockSet
from twcc.services.s3_tools import S3
from twcc.util import pp, table_layout, SpinCursor, isNone
from twcc.services.base import acls, users, image_commit, Keypairs
from twcc import GupSiteBlockSet, Session2


def create_vcs(name, sol, img_name, network,
               keypair, flavor, sys_vol, fip):

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
        raise ValueError("Missing parameter: `--name`.")

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
        raise ValueError("Missing parameter: `--key`.")
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

    # x-extra-property-volume-type
    # required['x-extra-property-volume-type'] = ""

    # x-extra-property-availability-zone
    required['x-extra-property-availability-zone'] = "nova"

    # for ele in extra_props:
    #    if not ele in required:
    #        print(ele, "!!!"*3)
    #        required[ele] = extra_props[ele]

    print("create vm")
    print(required)
    return vcs.create(name, exists_sol[sol], required)


def doSiteReady(site_id):
    b = Sites(debug=False)
    wait_ready = False
    while not wait_ready:
        print("Waiting for container to be Ready.")
        if b.isReady(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id


def create_bucket(bucket_name):
    s3 = S3()
    s3.create_bucket(bucket_name)


def create_cntr(cntr_name, gpu, sol_name, sol_img, isWait):
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
    print(imgs)
    if type(sol_img) == type(None) or len(sol_name) == 0:
        def_header['x-extra-property-image'] = imgs[0]
    else:
        if sol_img in imgs:
            def_header['x-extra-property-image'] = sol_img
        else:
            raise ValueError(
                "Container image '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    res = b.create(cntr_name, sol_id, def_header)
    if 'id' not in res.keys():
        if 'message' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['message']))
        if 'detail' in res:
            raise ValueError(
                "Can't find id, please check error message : {}".format(res['detail']))
    else:
        print("SiteId: {0}.".format(res['id']))

    if isWait:
        doSiteReady(res['id'])
    return int(res['id'])

# end original function ==================================================

# Create groups for command
@click.group(help="Create Service")
def cli():
    pass

@click.command(context_settings=dict(max_content_width=500) , help="vcs(Virtual Compute Service)")
@click.option('-key', '--keypair', 'keypair', flag_value='Keypair',
              help="Delete existing keypair(s) for VCS.")
@click.option('-name', 'name', default="twccli", type=str,
              help="Enter name for your resources.")
@click.option('-sys-vol', '--system-volume-type', 'sys_vol', default="SSD", type=str,
              help="Chose system volume disk type. [VCS only]", show_default=True)
@click.option('-flvr', '--flavor-name', 'flavor', default="v.2xsuper", type=str,
              help="Chose hardware configuration. -VCS only-", show_default=True)
@click.option('-img', '--img_name', 'img_name', default=None, type=str,
              help="Enter image name.")
@click.option('--wait/--nowait', '--wait_ready/--no_wait_ready', 'wait', is_flag=True, default=False,
              help='Wait until resources are provisioned')
@click.option('-net', '--network', 'network', default=None, type=str,
              help="Enter network name. -VCS only-")
@click.option('-fip/-nofip', '--need-floating-ip/--no-need-floating-ip', 'fip', is_flag=True, default=False,
              help='Set this flag for applying a floating IP. -VCS only-')
@click.argument('ids_or_names', nargs=-1)
def vcs(keypair, name, ids_or_names, sys_vol, flavor, img_name, wait, network, fip):

    if name == 'twccli' and not len(ids_or_names) == 0:
        name = ids_or_names[0]

    if isNone(name) or name == 'twccli':
        raise ValueError("`--n` is required.")

    if not isNone(sys_vol) & isNone(flavor):

        if sys_vol == "TensorFlow":
            sys_vol = "ubuntu"
        ans = create_vcs(name, sys_vol, img_name, network, keypair,
                         flavor, sys_vol, fip)
        if wait:
            doSiteReady(ans['id'], site_type='vcs')
        print(ans)
        return True

    keyring = Keypairs()

    if 'name' in keyring.queryById(name):
        raise ValueError("Duplicated name for keypair")

    print(Session2._getTwccDataPath())
    keyring.createKeyPair(name)


@click.option('--name', 'name', default="twccli", type=str,
              help="Enter name for your resources.")
@click.command(help="cos(Cloud Object Storage)")
def cos(name):
    create_bucket(name)

# end object ===============================================================


@click.command(help="ccs(Container Computer Service)")
@click.option('-name', '--name', 'name', default="twccli", type=str,
              help="Enter name for your resources.")
@click.option('-gpu', '--gpu-number', 'gpu', default=1, type=int,
              help="Enter desire number for GPU.")
@click.option('-sol', '--solution', 'sol', default="TensorFlow", type=str,
              help="Enter TWCC solution name.")
@click.option('-img', '--img-name', 'img_name', default=None, type=str,
              help="Enter image name. Please check through `twccli ls t cos -img`")
@click.option('-wait/-nowait', '--wait-ready/--no-wait-ready', 'wait', is_flag=True, default=False,
              help='Wait until resources are provisioned')
def ccs(name, gpu, sol, img_name, wait):
    create_cntr(name, gpu, sol, img_name, wait)


cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)


def main():
    cli()


if __name__ == "__main__":
    main()
