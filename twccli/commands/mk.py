# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import time
from datetime import datetime
from twccli.twcc.services.compute import GpuSite as Sites
from twccli.twcc.services.compute import VcsSite, VcsSecurityGroup, VcsImage
from twccli.twcc.services.solutions import solutions
from twccli.twcc import GupSiteBlockSet
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.util import pp, table_layout, SpinCursor, isNone, jpp, mk_names, isFile
from twccli.twcc.services.base import acls, users, image_commit, Keypairs
from twccli.twcc import GupSiteBlockSet, Session2


def create_commit(site_id, tag, isAll=False):
    ccs = Sites()

    site = ccs.getDetail(site_id)
    if 'Pod' in site:
        img_name = site['Pod'][0]['container'][0]['image'].split(
            '/')[-1].split(":")[0]
        c = image_commit()
        return c.createCommit(site_id, tag, img_name)


def create_vcs(name, sol="", img_name="", network="",
               keypair="", flavor="", sys_vol="", fip=""):
    """Create vcs
    create vcs by set solution, image name, flavor
    create vcs by default value

    :param sys_vol: Chose system volume disk type
    :type sys_vol: string
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

    # x-extra-property-volume-type
    # required['x-extra-property-volume-type'] = ""

    # x-extra-property-availability-zone
    required['x-extra-property-availability-zone'] = "nova"


    return vcs.create(name, exists_sol[sol], required)


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


def create_bucket(bucket_name):
    """Create bucket by name

    :param bucket_name: Enter bucket name
    :type bucket_name: string
    """
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
@click.group(help="Create (allocate) your TWCC resources.")
def cli():
    pass


@click.command(context_settings=dict(max_content_width=500),
               help="Create your VCS (Virtual Compute Service) instances.")
@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of the instance.")
@click.option('-s', '--site-id', 'site_id', type=str,
              help="ID of the instance.")
@click.option('-fip', '--need-floating-ip', 'fip',
              is_flag=True, default=False,  flag_value=True,
              help='Assign a floating IP to the instance.')
@click.option('-flvr', '--flavor-name', 'flavor', default="v.2xsuper", type=str,
              show_default=True,
              help="The hardware configuration.")
@click.option('-img', '--img_name', 'img_name', default=None, type=str,
              help="Name of the image.")
@click.option('-itype', '--image-type-name', 'sol', default="Ubuntu", type=str,
              help="Name of the image type.")
@click.option('-key', '--keypair', 'keypair',
              help="Name of the key pair for access your instance.")
@click.option('-net', '--network', 'network', default=None, type=str,
              help="Name of the network.")
@click.option('-snap', '--snapshots', 'snapshot', is_flag=True,
              default=False,
              help="Create a snapshot for an instance. `-s` is required!")
@click.option('-sys-vol', '--system-volume-type', 'sys_vol', default="SSD", type=str,
              show_default=True,
              help="Volume type of the boot volume.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-wait', '--wait-ready', 'wait',
              is_flag=True, default=False, flag_value=True,
              help='Wait until your instance to be provisioned.')
@click.argument('ids_or_names', nargs=-1)
@click.pass_context
def vcs(ctx, keypair, name, ids_or_names, site_id, sys_vol, flavor, img_name, wait, network, snapshot, sol, fip, is_table):
    """Command line for create VCS

    :param keypair: Delete existing keypair(s)
    :type keypair: string
    :param name: Enter name for your resources
    :type name: string
    :param sys_vol: Chose system volume disk type
    :type sys_vol: string
    :param flavor: Choose hardware configuration
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
    :param fip: Set this flag for applying a floating IP
    :type fip: bool
    :param is_table: Set this flag table view or json view
    :type is_table: bool
    :param ids_or_names: Enter ids or names
    :type ids_or_names: string or tuple
    """

    if snapshot:
        sids = mk_names(site_id, ids_or_names)
        if not isNone(sids) or len(sids) > 0:
            sid = sids[0]
            print("create snapshot for {}".format(sid))
            img = VcsImage()
            desc_str = "twccli created at {}".format(
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            if name == 'twccli':
                name += datetime.now().strftime("%d%m%H%M")
            return img.createSnapshot(sid, name, desc_str)

    else:
        if name == 'twccli':
            name = "{}_{}".format(name, flavor)
        ans = create_vcs(name, sol=sol.lower(), img_name=img_name, network=network, keypair=keypair,
                         flavor=flavor, sys_vol=sys_vol, fip=fip)
        ans["solution"] = sol
        ans["flavor"] = flavor

        if wait:
            doSiteReady(ans['id'], site_type='vcs')

        if is_table:
            cols = ["id", "name", "status"]
            table_layout("VCS Site", ans, cols, isPrint=True)
        else:
            jpp(ans)


@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of the bucket.")
@click.command(help="Create your COS (Cloud Object Service) buckets.")
def cos(name):
    """Command line for create cos

    :param name: Enter name for your resources.
    :type name: string
    """
    create_bucket(name)


@click.command(help="Create your key pairs.")
@click.option('-n', '--name', 'name', default="twccli", type=str,
              help="Name of your instance.")
def key(name):
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
        with open(wfn, "w") as fp:
            fp.write(ans)
        import os
        os.chmod(wfn, 0o600)
        print("Your keypair is in `{}` with mode 600".format(wfn))


# end object ===============================================================


@click.command(help="'Make' Operations for CCS (Container Computer Service)")
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
def ccs(name, gpu, sol, img_name, wait, req_dup, siteId, dup_tag, is_table):
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
            doSiteReady(ans['id'])

        if is_table:
            cols = ["id", "name", "status"]
            table_layout("CCS Site:{}".format(
                ans['id']), ans, cols, isPrint=True)
        else:
            jpp(ans)


cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)
cli.add_command(key)


def main():
    cli()


if __name__ == "__main__":
    main()
