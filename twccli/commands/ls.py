# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
import re
import sys
import datetime
import jmespath
from twccli.twcc.session import Session2
from twccli.twcc.util import pp, jpp, table_layout, SpinCursor, isNone, mk_names, mkCcsHostName, timezone2local
from twccli.twcc.services.compute import GpuSite, VcsSite, VcsSecurityGroup, VcsImage, VcsServer, Volumes, LoadBalancers, Fixedip
from twccli.twcc.services.compute import getServerId, getSecGroupList
from twccli.twcc.services.compute_util import list_vcs, list_vcs_img
from twccli.twcc import GupSiteBlockSet
from twccli.twcc.services.solutions import solutions
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.services.network import Networks
from twccli.twcc.services.base import acls, users, image_commit, Keypairs
from twccli.twcc.services.generic import GenericService
from twccli.twccli import pass_environment, logger
from click.core import Group


def CatchAllExceptions(cls, handler):

    class Cls(Group):

        _original_args = None

        def make_context(self, info_name, args, parent=None, **extra):
            # grab the original command line arguments
            self._original_args = ' '.join(args)
            try:
                return super(Cls, self).make_context(
                    info_name, args, parent=parent, **extra)
            except Exception as exc:
                # call the handler
                handler(self, info_name, exc)

                # let the user see the original error
                raise

        def invoke(self, ctx):
            try:
                return super(Cls, self).invoke(ctx)
            except Exception as exc:
                # call the handler
                handler(self, ctx.info_name, exc)
                # let the user see the original error
                raise
    return Cls


def handle_exception(cmd, info_name, exc):
    # send error info to rollbar, etc, here
    click.echo(':: Command line: {} {}'.format(info_name, cmd._original_args))
    click.echo(':: Raised error: {}'.format(exc))


def refactor_ip_detail(ans, vnet_id2name):
    net = Networks()
    for each_ans in ans:
        occupied_resource_type = jmespath.search(
            'occupied_resource.type', each_ans)
        occupied_resource_type_id = jmespath.search(
            'occupied_resource.id', each_ans)
        if isNone(occupied_resource_type_id) or isNone(occupied_resource_type):
            each_ans['occupied_resource_type_id'] = ''
        else:
            each_ans['occupied_resource_type_id'] = occupied_resource_type + \
                ':'+occupied_resource_type_id
        vnet_name = ''
        if not each_ans['private_net'] in vnet_id2name:
            vnet_name = net.queryById(each_ans['private_net'])['name']
            vnet_id2name[each_ans['private_net']] = vnet_name
        else:
            vnet_name = vnet_id2name[each_ans['private_net']]
        each_ans['vnet'] = vnet_name


def list_fixed_ips(site_ids_or_names, column, filter_type, is_table):
    fxip = Fixedip()
    ans = []
    vnet_id2name = {}
    cols = ['id', 'address',  'create_time', 'status',
            'type', 'occupied_resource_type_id', 'vnet']
    if not column == '':
        cols = column.split(',')
        cols.append('id')
        cols.append('address')
        cols = list(set(cols))
    if len(site_ids_or_names) > 0:
        for ip_id in site_ids_or_names:
            ans.append(fxip.list(ip_id=ip_id))
    else:
        ans = fxip.list(filter=filter_type)
    refactor_ip_detail(ans, vnet_id2name)
    if len(ans) > 0:
        if is_table:
            table_layout("IP Results",
                         ans,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(ans)


def list_load_balances(site_ids_or_names, column, is_all, is_table):
    vlb = LoadBalancers()
    ans = []
    if len(site_ids_or_names) > 0:
        if column == '':
            cols = ['id', 'name',  'create_time', 'status', 'vip', 'pools_method',
                    'members_IP,status', 'listeners_name,protocol,port,status', 'private_net_name']
        else:
            cols = column.split(',')
            if not 'id' in cols:
                cols.append('id')
            if not 'name' in cols:
                cols.append('name')
        for vlb_id in site_ids_or_names:
            ans.append(vlb.list(vlb_id))
    else:
        if column == '':
            cols = ['id', 'name',  'create_time',
                    'private_net_name', 'status', 'pools_method']
        else:
            cols = column.split(',')
            if not 'id' in cols:
                cols.append('id')
            if not 'name' in cols:
                cols.append('name')
        ans = vlb.list(isAll=is_all)
    for this_ans in ans:
        if 'detail' in this_ans:
            is_table = False
            continue
        this_ans['private_net_name'] = this_ans['private_net']['name']
        this_ans['pools_method'] = ','.join(
            [this_ans_pool['method'] for this_ans_pool in this_ans['pools']])
    if len(site_ids_or_names) > 0:
        for this_ans in ans:
            if 'detail' in this_ans:
                is_table = False
                continue
            for this_ans_pool in this_ans['pools']:
                this_ans['members_IP,status'] = ['({}:{},{})'.format(this_ans_pool_members['ip'], this_ans_pool_members['port'],
                                                                     this_ans_pool_members['status']) for this_ans_pool_members in this_ans_pool['members']]

            this_ans['listeners_name,protocol,port,status'] = ['{},{},{},{}'.format(
                this_ans_listeners['name'], this_ans_listeners['protocol'], this_ans_listeners['protocol_port'], this_ans_listeners['status']) for this_ans_listeners in this_ans['listeners']]
    if len(ans) > 0:
        if is_table:
            table_layout("Load Balancers Result",
                         ans,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(ans)


def list_volume(site_ids_or_names, is_all, is_table):
    vol = Volumes()
    ans = []
    cols = ['id', 'name', 'size', 'create_time', 'volume_type',
            'status', 'mountpoint']
    if len(site_ids_or_names) > 0:
        for vol_id in site_ids_or_names:
            ans.append(vol.list(vol_id))
        for the_vol in ans:
            if 'detail' in the_vol:
                is_table = False
                continue
            if len(the_vol['name']) > 15:
                the_vol['name'] = '-'.join(the_vol['name'].split('-')
                                           [:2])+'...'
            if 'mountpoint' in the_vol and len(the_vol['mountpoint']) == 1:
                the_vol['mountpoint'] = the_vol['mountpoint'][0]
    else:
        ans = vol.list(isAll=is_all)
        for the_vol in ans:
            if 'detail' in the_vol:
                is_table = False
                continue
            if len(the_vol['name']) > 15:
                the_vol['name'] = '-'.join(the_vol['name'].split('-')
                                           [:2])+'...'
            if 'mountpoint' in the_vol and len(the_vol['mountpoint']) == 1:
                the_vol['mountpoint'] = the_vol['mountpoint'][0]
    if len(ans) > 0:
        if is_table:
            table_layout("VDS Result",
                         ans,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(ans)


def list_vcs_sol(is_table):
    ans = VcsSite.getSolList(mtype='list', name_only=True)
    if is_table:
        print("Avbl. VCS Image Types: {}".format(", ".join(ans)))
    else:
        jpp(ans)


def list_snapshot(site_ids_or_names, is_all, is_table, desc):
    ans = []
    if not len(site_ids_or_names) == 0:
        for i, sid in enumerate(site_ids_or_names):
            # sid = site_ids_or_names[0]
            img = VcsImage()
            srv_id = getServerId(sid)
            images = img.list(srv_id)
            if not images:
                continue
            [image.setdefault('site_id', sid) for image in images]
            ans.extend(images)
            cols = ['id', 'site_id', 'name', 'status', 'create_time']
    else:
        img = VcsImage()
        ans = img.list(isAll=is_all)
        cols = ['id', 'name', 'status', 'create_time']
    if len(ans) > 0:
        if is_table:
            table_layout("Snapshot Result",
                         ans,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(ans)


def list_gpu_log(site_ids_or_names):
    a = GpuSite()
    site_log = {}
    for site_id in site_ids_or_names:
        log = a.getLog(site_id)
        site_log[site_id] = log
    jpp(site_log)


def list_gpu_flavor(is_table=True):
    ans = GpuSite.getGpuList()
    formated_ans = [{"`-gpu` tag": x, "description": ans[x]} for x in ans]
    if is_table:
        table_layout("Existing `-gpu` flavor",
                     formated_ans,
                     isPrint=True,
                     isWrap=False)
    else:
        jpp(ans)


def list_gpu_flavor_online(solution_name, is_table=True):
    gpu_tag2spec = GpuSite().getGpuList()
    formated_ans = [{"`-gpu` tag": x, "description": gpu_tag2spec[x]}
                    for x in gpu_tag2spec]
    if is_table:
        table_layout("Existing `-gpu` flavor",
                     formated_ans,
                     isPrint=True,
                     isWrap=False)
    else:
        jpp(gpu_tag2spec)


def list_vcs_flavor(is_table=True):
    wanted_ans = [
        {"flavor name": "v.super", "spec": "02vCPU+016gMEM+100gHDD"},
        {"flavor name": "v.xsuper", "spec": "04vCPU+032gMEM+100gHDD"},
        {"flavor name": "v.2xsuper", "spec": "08vCPU+064gMEM+100gHDD"},
        {"flavor name": "v.4xsuper", "spec": "16vCPU+128gMEM+100gHDD"},
        {"flavor name": "v.8xsuper", "spec": "32vCPU+256gMEM+100gHDD"},
    ]
    if is_table:
        table_layout("VCS Product Types",
                     wanted_ans, ['flavor name', 'spec'],
                     isPrint=True,
                     isWrap=False)
    else:
        jpp(wanted_ans)


def list_port(site_id, is_table=True, is_print=True):
    """List port by site id, print information in table/json format

    :param site_id: list of site id
    :type site_id: string or tuple
    :param is_table: Show information in Table view or JSON view.
    :type is_table: bool
    :param is_print: do proint or not
    :type is_print: bool
    """
    b = GpuSite()
    ans = b.getConnInfo(site_id, ssh_info=False)
    if is_table:
        table_layout("Port info. for {}".format(site_id), ans, isPrint=True)
    else:
        if is_print:
            jpp(ans)
        else:
            return ans


def list_addr(site_id):
    return mkCcsHostName(GpuSite().getDetail(site_id)["Service"][0]
                         ["annotations"]["allocated-public-ip"])


def list_commit():
    """List copy image by site id
    """
    c = image_commit()
    print(c.getCommitList())


def list_all_img(solution_name, is_table=True):
    """List all image by solution name

    :param solution_name: Enter name for your resources.
    :type solution_name: string
    """
    print("Note : this operation take 1-2 mins")
    a = solutions()
    if isNone(solution_name) or len(solution_name) == 0:
        cntrs = [(cntr['name'], cntr['id']) for cntr in a.list()
                 if not cntr['id'] in GupSiteBlockSet]
    else:
        if len(solution_name) == 1:
            solution_name = solution_name[0]
            cntrs = [(cntr['name'], cntr['id']) for cntr in a.list()
                     if not cntr['id'] in GupSiteBlockSet
                     and cntr['name'].lower() == solution_name.lower()]

    sol_list = GpuSite.getSolList(name_only=True)
    base_site = GpuSite(debug=False)
    output = []
    for (sol_name, sol_id) in cntrs:
        output.append({
            "sol_name": sol_name,
            "sol_id": sol_id,
            "images": base_site.getAvblImg(sol_id, sol_name)
        })

    if is_table:
        table_layout("img", output, ['sol_name',
                                     'sol_id', 'images'], isPrint=True)
    else:
        jpp(output)


def list_cntr(site_ids_or_names, is_table, isAll):
    """List container by site ids in table/json format or list all containers

    :param site_ids_or_names: list of site id
    :type site_ids_or_names: string or tuple
    :param is_table: Show information in Table view or JSON view.
    :type is_table: bool
    :param is_all: List all the containers in the project. (Tenant Administrators only)
    :type is_all: bool
    """
    col_name = ['id', 'name', 'create_time', 'status']
    a = GpuSite()

    if len(site_ids_or_names) == 0:
        my_GpuSite = a.list(isAll=isAll)
    else:
        col_name = ['id', 'name', 'create_time', 'status', 'flavor', 'image']
        my_GpuSite = []
        for ele in site_ids_or_names:
            # site_id = int(ele)
            ans = a.queryById(ele)
            ans_info = a.getDetail(ele)
            ans_flavor = jmespath.search('Pod[0].flavor', ans_info)
            if not ans_flavor == None:
                ans['flavor'] = ans_flavor
            ans_image = jmespath.search('Pod[0].container[0].image', ans_info)
            if not ans_image == None and '/' in ans_image:
                ans['image'] = ans_image.split('/')[-1]
            my_GpuSite.append(ans)
    my_GpuSite = [i for i in my_GpuSite if 'id' in i]
    if len(my_GpuSite) > 0:
        if isAll:
            col_name.append('user')

        if is_table:
            table_layout('GpuSite',
                         my_GpuSite,
                         caption_row=col_name,
                         isPrint=True)
        else:
            jpp(my_GpuSite)
    else:
        if is_table:
            table_layout('GpuSite', [], caption_row=col_name, isPrint=True)
        else:
            jpp([])


def list_buckets(is_table, versioning):
    """List buckets in table/json format

    :param is_table: Show information in Table view or JSON view.
    :type is_table: bool
    """
    s3 = S3()
    buckets = s3.list_bucket(show_versioning=versioning)
    if is_table:
        table_layout("COS buckets {}", buckets, isWrap=False, isPrint=True)
    else:
        jpp(buckets)


def show_dict(obj):
    for obj_key in obj.keys():
        print("== %s ==" % (obj_key))
        print(obj[obj_key])


def list_files(ids_or_names, okey_regex=None, is_public=True, is_table=True):
    """List file in specific folder in buckets table/json format

    :param ids_or_names: list of site id
    :type ids_or_names: string or tuple
    :param name: Enter name for your resources.
    :type name: string
    :param is_table: Show information in Table view or JSON view.
    :type is_table: bool
    """
    import re
    s3 = S3()

    for bucket_name in ids_or_names:
        files = s3.list_object(bucket_name)

        if not isNone(okey_regex):
            files = [mfile for mfile in files if re.search(
                okey_regex, mfile[u'Key'])]  # 會不會中招呀!?

        if is_public:
            more_details = []
            for mfile in files:
                mdata = mfile
                mdata['is_public'] = s3.get_object_info(
                    bucket_name, mfile[u'Key'])['is_public_read']
                more_details.append(mdata)
            files = more_details

        col_caption = ['LastModified', 'Key', 'Size', 'is_public'] if is_public else [
            'LastModified', 'Key', 'Size']
        is_versioning = False
        ver_info = s3.get_versioning(bucket_name)
        if u'Status' in ver_info and ver_info[u'Status'] == "Enabled":
            is_versioning = True
            col_caption.append('Versioning')

        if is_table and not isNone(files):
            bkt_state = "%s (Versioing: On)" % (
                bucket_name) if is_versioning else bucket_name
            table_layout("COS objects {}".format(bkt_state),
                         files,
                         isWrap=False,
                         max_len=30,
                         isPrint=True,
                         captionInOrder=True,
                         caption_row=col_caption)
        else:
            jpp(files)


def list_secg(ids_or_names, is_table=True):
    """List security group by site ids in table/json format

    :param site_ids_or_names: list of site id
    :type site_ids_or_names: string or tuple
    :param name: Enter name for your resources.
    :type name: string
    :param is_table: Show information in Table view or JSON view.
    :type is_table: bool
    """
    if not len(ids_or_names) > 0:
        raise ValueError("Need resource id for listing security group")

    if len(ids_or_names) == 1:
        secg_list = getSecGroupList(ids_or_names[0])
        secg_id = secg_list['id']
        secg_detail = secg_list['security_group_rules']
        if is_table:
            table_layout("SecurityGroup for {}".format(ids_or_names[0]),
                         secg_detail,
                         caption_row=[
                             'id', 'port_range_min', 'port_range_max', 'remote_ip_prefix', 'direction'],
                         isPrint=True, captionInOrder=True)
        else:
            jpp(secg_detail)
        return True


def list_ccs_with_properties(res_property, site_ids_or_names, product_type, is_table=True):
    if res_property == 'flavor':
        list_gpu_flavor(is_table)

    if res_property == 'image':
        if not product_type:
            list_all_img(site_ids_or_names, is_table)
        else:
            if len(site_ids_or_names) == 1:
                list_gpu_flavor_online(site_ids_or_names[0])
            else:
                list_gpu_flavor_online('all')

    if res_property == 'commit':
        list_commit()

    if res_property == "solution":
        avbl_sols = GpuSite().getSolList(mtype='list', name_only=True)
        click.echo("Avalible Image types for CCS: {}".format(
            ", ".join(avbl_sols)))

    if res_property == 'log':
        list_gpu_log(site_ids_or_names)


# end orginal function ====================================

# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="List your TWCC resources.")
def cli():
    try:
        ga = GenericService()
        func_call = '_'.join([i for i in sys.argv[1:] if re.findall(
            r'\d', i) == [] and not i == '-sv']).replace('-', '')
        ga._send_ga(func_call)
    except Exception as e:
        logger.warning(e)
    pass


@click.command(
    help="'List' details of your VCS (Virtual Compute Service) instances.")
@click.option('-n',
              '--name',
              'name',
              default=None,
              type=str,
              help="Name of the instance.")
@click.option('-s', '--site-id', 'name', type=str, help="ID of the instance.")
@click.option('-all',
              '--show-all',
              'is_all',
              is_flag=True,
              type=bool,
              help="List all the instances in the project.")
@click.option('-col',
              '--column',
              'column',
              default='',
              help='User define table column. ex: twccli ls vcs -col desc / twccli ls vcs -col user.display_name')
@click.option('-img',
              '--image',
              'res_property',
              flag_value='image',
              help='View all image files. Provid solution name for filtering.')
@click.option('-itype',
              '--image-type',
              'res_property',
              default=None,
              flag_value='solution',
              help="List VCS image types.")
@click.option('-key',
              '--keypair',
              'res_property',
              flag_value='Keypair',
              help="List your keypairs in TWCC VCS. Equals to `ls key`")
@click.option('-net',
              '--network',
              'res_property',
              flag_value='Network',
              help="Using 'ls vnet' next version, List existing network in TWCC VCS.")
@click.option('-ptype',
              '--product-type',
              'res_property',
              flag_value='flavor',
              help="List VCS available product types (hardware configuration)."
              )
@click.option('-secg',
              '--security-group',
              'res_property',
              flag_value='SecurityGroup',
              help="List existing security groups for VCS instance.")
@click.option('-cus-img',
              '--custom-image',
              'res_property',
              flag_value='Snapshot',
              help="List custom images for the instance. `-s` is required!")
@click.option('-table / -json',
              '--table-view / --json-view',
              'is_table',
              is_flag=True,
              default=True,
              show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('site_ids_or_names', nargs=-1)
@pass_environment
@click.pass_context
# @click.pass_context ctx,
# @logger.catch
# @exception(logger)
def vcs(ctx, env, res_property, site_ids_or_names, name, column, is_table, is_all):
    """Command line for List VCS
    Function list :
    1. list port
    2. list commit
    3. list all image
    4. list containers
    5. list buckets
    6. list files in specific foder
    7. list security group by site

    :param res_property: Funtion type (network, keypair, solution, image)
    :type res_property: string
    :param site_ids_or_names: list of site id
    :type site_ids_or_names: string or tuple
    :param name: Enter name for your resources.
    :type name: string
    :param is_table: Show information in Table view or JSON view.
    :type is_table: bool
    :param is_all: List all the containers in the project. (Tenant Administrators only)
    :type is_all: bool
    """
    site_ids_or_names = mk_names(name, site_ids_or_names)
    if isNone(res_property):
        list_vcs(site_ids_or_names, is_table, column=column, is_all=is_all)

    if res_property == 'Snapshot':
        desc_str = "twccli_{}".format(
            datetime.datetime.now().strftime("_%m%d%H%M"))
        list_snapshot(site_ids_or_names, is_all, is_table, desc_str)

    if res_property == 'image':
        list_vcs_img(site_ids_or_names, is_table)

    if res_property == 'flavor':
        list_vcs_flavor(is_table)

    if res_property == "solution":
        list_vcs_sol(is_table)

    if res_property == 'Network':
        net = Networks()
        if len(site_ids_or_names) > 0:
            ans = [net.queryById(x) for x in site_ids_or_names]
            cols = [
                "id", "name", "cidr", "create_time", "gateway", "nameservers",
                "status", "user"
            ]
        else:
            ans = net.list()
            cols = ["id", "name", "cidr", "create_time", "status"]
        if is_table:
            table_layout("VCS Networks", ans, cols, isPrint=True)
        else:
            jpp(ans)

    if res_property == 'SecurityGroup':
        list_secg(site_ids_or_names, is_table)

    if res_property == 'Keypair':
        ctx.invoke(key,
                   ids_or_names=site_ids_or_names,
                   name=name,
                   is_table=is_table)


# end vcs ==================================================
@click.command(
    help="'List' details of your COS (Cloud Object Storage) buckets.")
@click.option('-bkt',
              '--bucket-name',
              'name',
              default=None,
              type=str,
              help="Name of the Bucket.")
@click.option('-okey',
              '--object-key-name',
              'okey',
              default=None,
              type=str,
              help="Name of specific object key. Regular Expression compatible.")
@click.option('-pub / -nopub',
              '--show-public-status / --no-show-public-status',
              'is_public',
              is_flag=True,
              default=False,
              show_default=True,
              help="Show is public allow to read.")
@click.option('-table / -json',
              '--table-view / --json-view',
              'is_table',
              is_flag=True,
              default=True,
              show_default=True,
              help="Show information in Table view or JSON view.")
@click.option('-ver',
              '--check-versioning',
              'versioning',
              is_flag=True,
              default=None,
              help="Get versioning is enabled or not.")
@click.argument('ids_or_names', nargs=-1)
@pass_environment
def cos(env, name, okey, is_public, is_table, versioning, ids_or_names):
    """Command line for List COS
       Functions:
       1. list bucket
       2. list files in specific folder in bucket
    """

    ids_or_names = mk_names(name, ids_or_names)
    if len(ids_or_names) == 0:
        list_buckets(is_table, versioning)
    else:
        list_files(ids_or_names, okey_regex=okey,
                   is_public=is_public, is_table=is_table)


# end object ==================================================
@click.command(
    help="'List' the details of your CCS (Container Computer Service) containers.")
@click.option('-p',
              '--port',
              'show_ports',
              is_flag=True,
              help='Show port information.')
@click.option('-s', '--site-id', 'name', type=str, help="ID of the CCS.")
@click.option(
    '-all',
    '--show-all',
    'is_all',
    is_flag=True,
    type=bool,
    help="List all the containers in the project. (Tenant Administrators only)"
)
@click.option('-dup',
              '--show-duplication-status',
              'res_property',
              flag_value='commit',
              help='List the submitted requests of duplicating containers.')
@click.option('-gpu',
              '--gpus-flavor',
              'res_property',
              flag_value='flavor',
              help='List CCS available GPU environments.')
@click.option(
    '-gjpnb',
    '--get-jupyter-notebook',
    'get_info',
    default=None,
    flag_value='jpnb',
    help="Get entry points for Jupyter Note Service. `-s` is required!")
@click.option(
    '-gssh',
    '--get-ssh-info',
    'get_info',
    default=None,
    flag_value='ssh',
    help="Get entry points for Security Shell service. `-s` is required!")
@click.option('-img',
              '--image',
              'res_property',
              flag_value='image',
              help='List all CCS image name.')
@click.option('-log',
              '--log',
              'res_property',
              flag_value='log',
              help='List CCS log.')
@click.option('-itype',
              '--image-type-name',
              'res_property',
              default=None,
              flag_value='solution',
              help='List all CCS image types.')
@click.option('-ptype',
              '--product-type',
              is_flag=True,
              default=False,
              help="List CCS available product types (hardware configuration)."
              )
@click.option('-table / -json',
              '--table-view / --json-view',
              'is_table',
              is_flag=True,
              default=True,
              show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('site_ids_or_names', nargs=-1)
@pass_environment
# @click.pass_context ctx,
def ccs(env, res_property, name, product_type, site_ids_or_names, is_table, is_all,
        show_ports, get_info):
    """Command line for List Container
       Functions:
       1. list container
       2. list container image
       3. list image copy
       4. list solution
    """

    site_ids_or_names = mk_names(name, site_ids_or_names)
    if res_property in ['flavor', 'image', 'commit', 'solution', 'log']:
        list_ccs_with_properties(
            res_property, site_ids_or_names, product_type, is_table)
    elif isNone(res_property):
        if product_type:
            list_gpu_flavor_online('all')
        elif show_ports:
            if len(site_ids_or_names) == 1:
                list_port(site_ids_or_names[0], is_table)
            else:
                raise ValueError("Need only one resource id.")
        elif not isNone(get_info):
            if get_info == "ssh":
                ports = list_port(site_ids_or_names[0], False, False)
                ssh_port = [
                    x["port"] for x in ports if x["target_port"] == 22
                ][0]
                hostname = list_addr(site_ids_or_names[0])
                username = Session2._whoami()['username']
                click.echo("%s@%s -p %s" % (username, hostname, ssh_port))
            elif get_info == "jpnb":
                b = GpuSite()
                access_token = b.getJpnbToken(site_ids_or_names[0])
                ports = list_port(site_ids_or_names[0], False, False)
                ssh_port = [
                    x["port"] for x in ports if x["target_port"] == 8888
                ][0]
                hostname = list_addr(site_ids_or_names[0])
                click.echo("https://%s:%s?token=%s" %
                           (hostname, ssh_port, access_token))

        else:
            list_cntr(site_ids_or_names, is_table, is_all)


@click.command(help='List your keypairs in VCS.')
@click.option('-n',
              '--name',
              'name',
              default=None,
              type=str,
              help="Enter name for your resource name")
@click.option('-table / -json',
              '--table-view / --json-view',
              'is_table',
              is_flag=True,
              default=True,
              show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@pass_environment
# @click.pass_context ctx,
def key(env, name, is_table, ids_or_names):
    """Command line for List Key
    """
    ids_or_names = mk_names(name, ids_or_names)

    keyring = Keypairs()
    if len(ids_or_names) > 0:
        ans = []
        cols = ['name', 'fingerprint', 'create_time', 'user']
        for ele in ids_or_names:
            ans.append(keyring.queryById(ele))
    else:
        cols = ['name', 'fingerprint']
        ans = keyring.list()

    if is_table:
        table_layout(' Existing Keypairs ',
                     ans,
                     cols,
                     isPrint=True,
                     isWrap=False)
    else:
        jpp(ans)


@click.option('-id', '--disk-id', 'name', type=int,
              help="Index of the disk.")
@click.option('-all',
              '--show-all',
              'is_all',
              is_flag=True,
              type=bool,
              help="List all the disks.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="List your VDS (Virtual Disk Service).")
@click.pass_context
def vds(ctx, name, ids_or_names, is_all, is_table):
    """Command line for list vds

    :param name: Enter name for your resources.
    :type name: string
    """
    ids_or_names = mk_names(name, ids_or_names)
    list_volume(ids_or_names, is_all, is_table)


@click.option('-id', '--virtual_network_id', 'vnetid', type=int,
              help="Index of the virtual network.")
@click.option('-all',
              '--show-all',
              'is_all',
              is_flag=True,
              type=bool,
              help="List all the virtual network.")
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="List your Virtual Network.")
@click.pass_context
def vnet(ctx, vnetid, ids_or_names, is_all, is_table):
    """Command line for list virtual network

    :param vnetid: Enter name for your resources.
    :type vnetid: string
    """
    ids_or_names = mk_names(vnetid, ids_or_names)
    net = Networks()
    if len(ids_or_names) > 0:
        ans = [net.queryById(x) for x in ids_or_names]
        cols = [
            "id", "name", "cidr", "create_time", "gateway", "nameservers",
            "status", "user"
        ]
    else:
        ans = net.list()
        cols = ["id", "name", "cidr", "create_time", "status"]
    if is_table:
        table_layout("VCS Networks", ans, cols, isPrint=True)
    else:
        jpp(ans)


@click.option('-id', '--vlb-id', 'vlb_id', type=int,
              help="Index of the volume.")
@click.option('-all',
              '--show-all',
              'is_all',
              is_flag=True,
              type=bool,
              help="List all the load balancers.")
@click.option('-col',
              '--column',
              'column',
              default='',
              help='User define table column. ex: twccli ls vlb -col pools[0].members')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="List your Load Balancers.")
@click.pass_context
def vlb(ctx, vlb_id, ids_or_names, column, is_all, is_table):
    """Command line for list vds

    :param vlb_id: Enter id for your load balancer.
    :type vlb_id: string
    :param ids_or_names: Enter more than one id for your load balancer.
    :type ids_or_names: string

    """
    ids_or_names = mk_names(vlb_id, ids_or_names)
    list_load_balances(ids_or_names, column, is_all, is_table)


@click.option('-id', '--fxip-id', 'ip_id', type=int,
              help="Index of the volume.")
@click.option('-fil', '--filter-type', type=click.Choice(['STATIC', 'DYNAMIC', 'ALL'], case_sensitive=False), default='STATIC', help="Filter the type.")
# @click.option('-all',
#               '--show-all',
#               'is_all',
#               is_flag=True,
#               type=bool,
#               help="List all the load balancers.")
@click.option('-col',
              '--column',
              'column',
              default='',
              help='User define table column. ex: twccli ls vlb -col pools[0].members')
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.argument('ids_or_names', nargs=-1)
@click.command(help="List your ips.")
@click.pass_context
def fxip(ctx, ip_id, filter_type, ids_or_names, column, is_table):
    """Command line for list vds

    :param ip_id: Enter id for your fixed ips.
    :type ip_id: string
    :param ids_or_names: Enter more than one id for your fixed ip.
    :type ids_or_names: string

    """
    ids_or_names = mk_names(ip_id, ids_or_names)
    list_fixed_ips(ids_or_names, column, filter_type, is_table)


cli.add_command(vcs)
cli.add_command(cos)
cli.add_command(ccs)
cli.add_command(key)
cli.add_command(vds)
cli.add_command(vnet)
cli.add_command(vlb)
cli.add_command(fxip)


def main():
    cli()


if __name__ == "__main__":
    main()
