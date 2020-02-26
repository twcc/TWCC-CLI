# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import time
from twcc.services.compute import GpuSite as Sites
from twcc.services.solutions import solutions
from twcc import GupSiteBlockSet
from twcc.services.s3_tools import S3
from twcc.util import pp, table_layout, SpinCursor, isNone
from twcc.services.base import acls, users, image_commit, Keypairs
from twcc import GupSiteBlockSet, Session2


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
@click.group(help="test")
def cli():
    pass

@click.option('-key', '--keypair', 'res_type_opt', flag_value='Keypair',
              help="Create or add a keypair for VCS.")
@click.option('--name', 'name', default="twccli", type=str,
              help="Enter name for your resources.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="abbr for vcs")
def v(res_type_opt, name, ids_or_names):
    if name=='twccli' and not len(ids_or_names)==0:
        name = ids_or_names[0]

    if isNone(name) or name=='twccli':
        raise ValueError("`--n` is required.")

    keyring = Keypairs()

    if 'name' in keyring.queryById(name):
        raise ValueError("Duplicated name for keypair")
    print(Session2._getTwccDataPath())
    keyring.createKeyPair(name)


@click.option('--name', 'name', default="twccli", type=str,
              help="Enter name for your resources.")
@click.command(help="abbr for cos")
def o(name):
    create_bucket(name)

# end object ===============================================================

@click.command(help="abbr for cntr")
@click.option('-name', '--name','name',default="twccli", type=str,
              help="Enter name for your resources.")
@click.option('--gpu', '--gpu_number', 'gpu', default=1, type=int,
              help="Enter desire number for GPU.")
@click.option('--sol', '--solution', 'sol', default="TensorFlow", type=str,
              help="Enter TWCC solution name.")
@click.option('--img', '--img_name', 'img_name', default=None, type=str,
              help="Enter image name. Please check through `twccli ls -t cos -img`")
@click.option('--wait/--nowait', '--wait_ready/--no_wait_ready', 'wait', is_flag=True, default=False,
 help='Wait until resources are provisioned')
def c(name, gpu, sol, img_name, wait):
    create_cntr(name, gpu, sol, img_name, wait)

cli.add_command(v)
cli.add_command(o)
cli.add_command(c)



def main():
    """
    this is a test main function
    """
    cli()


if __name__ == "__main__":
    main()
