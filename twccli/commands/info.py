# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import json
import re
import sys
import datetime
import jmespath
from twccli.twcc.session import Session2
from twccli.twcc.util import jpp, table_layout, sizeof_fmt
from twccli.twcc.services.base import acls, Users, image_commit, Keypairs, projects
from twccli.twcc.services.generic import GenericService, GpuService, CpuService

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
        if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
            logger.warning(e)
    pass


@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Get your HFS Information.")
@click.pass_context
def hfs(ctx, is_table):
    """Command line for info hfs

    """
    user = Users()
    user.getHFS(is_table)


@click.option(
    '-all',
    '--show-all',
    'is_all',
    is_flag=True,
    type=bool,
    help="Show information of all project that you joined."
)
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Get your project information.")
@click.pass_context
def proj(ctx, is_all, is_table):
    """Command line for info hfs

    """
    proj = projects()
    proj.getProjects(is_all, is_table)


@click.option(
    '-all',
    '--show-all',
    'is_all',
    is_flag=True,
    type=bool,
    help="List all quota information within this project. (Tenant Administrators only)"
)
@click.option('-table / -json', '--table-view / --json-view', 'is_table',
              is_flag=True, default=True, show_default=True,
              help="Show information in Table view or JSON view.")
@click.command(help="Get your quota Information.")
@click.pass_context
def quota(ctx, is_all, is_table):
    """Command line for info hfs

    """
    set_unlimited = lambda x: "unlimited" if x == -1 else x

    quota = {}

    quota_ccs = GpuService().getQuota(isAll=is_all)
    quota_vcs = CpuService().getQuota(isAll=is_all)

    if is_all:
        for x in quota_ccs:
            username = x[u'user'][u'username']
            quota[username] = {'CCS': x}

        for x in quota_vcs:
            username = x[u'user'][u'username']
            quota[username]['VCS'] = x

        if is_table:
            data = []
            for username in quota.keys():
                row = {}
                row['username'] = username
                for res_type in quota[username].keys():
                    row["%s-CPU"%(res_type)] = "%s / %s"%(quota[username][res_type][u'cpu'][u'usage'],
                                               set_unlimited(quota[username][res_type][u'cpu'][u'quota']) )
                    row["%s-GPU"%(res_type)] = "%s / %s"%(quota[username][res_type][u'gpu'][u'usage'],
                                               set_unlimited(quota[username][res_type][u'gpu'][u'quota']) )
                data.append(row)

            data = sorted(data, key=lambda x: int(x['VCS-CPU'].split(" /")[0]), reverse=True)
            col_cap = ['username', 'VCS-CPU', 'VCS-GPU', 'CCS-CPU', 'CCS-GPU']
            table_layout("Member Quota", data, isPrint=True, caption_row=col_cap, captionInOrder=True)
        else:
            jpp(quota)
    else:
        projq_vcs = quota_vcs[0]
        projq_ccs = quota_ccs[0]
        proj_name = projq_vcs['project']['name']

        vcs_list = {"CPU":"cpu", "GPU":"gpu",
                    "Floating IP":"floatingip",
                    "Memory": "memory"}
        quota = {}
        for ele in vcs_list.items():
            quota[ele[0]] = "%s / %s"%(projq_vcs[ele[1]][u'usage'],
                                      set_unlimited(projq_vcs[ele[1]][u'quota']) )

        if is_table:
            table_layout("[VCS QuotaPlan] for %s"%(proj_name), quota, isPrint=True)#, caption_row=col_cap, captionInOrder=True)


        ccs_list = {"CPU":"cpu", "GPU":"gpu",
                    "Memory": "memory"}
        quota = {}
        for ele in ccs_list.items():
            quota[ele[0]] = "%s / %s"%(projq_ccs[ele[1]][u'usage'],
                                      set_unlimited(projq_ccs[ele[1]][u'quota']) )


        if is_table:
            table_layout("[CCS QuotaPlan] for %s"%(proj_name), quota, isPrint=True)#, caption_row=col_cap, captionInOrder=True)


        if not is_table:
            quota = {"VCS": quota_vcs, "CCS":quota_ccs}
            jpp(quota)

cli.add_command(hfs)
cli.add_command(proj)
cli.add_command(quota)


def main():
    cli()


if __name__ == "__main__":
    main()
