#-*- coding: utf-8 -*-
from __future__ import print_function
"""NCHC TWCC-CLI command line tool

.. module:: twcc-cli
   :synopsis: A useful module indeed.
.. moduleauthor:: August Chao <1803001@narlabs.org.tw>
"""
#from twcc.twcc import TWCC
from twcc.services.base import acls,users,keypairs,projects,api_key
from twcc.services.jobs import jobs
from twcc.services.storage import images,volumes,snapshots,buckets
from twcc.util import pp

import click

# Create groups for command
@click.group()
def cli():
    pass

# Create a command for acls
@click.command()
@click.option('-l','--list','show_list',flag_value='list',help='Show the list of acls')
@click.option('-lg','--list_g','show_list',flag_value='list_g',help='Show the list of acls_g')
@click.option('-id','id_num',is_flag = None,help="The user id")
def Acls(show_list,id_num):
    '''
    Access control of IaaS
    '''
    acls_info = acls('sys',debug = False)

    if show_list == 'list':
        pp(list=acls_info.getSites())
    elif show_list == 'list_g':
        pp(list=acls_info.listGroup())

    if type(id_num) is not type(None):
        pp(list = acls_info.queryById(id_num))
    else:
        print_command_help(Acls)

# Create a command for users 
@click.command()
@click.option('-l','--list','show_list',is_flag=True,help="Show list of users")
@click.option('-id','id_num',is_flag = None,help="The user id")
def Users(show_list,id_num):
    '''
    Get user UUID for S3 bucket
    '''
    users_info = users('sys',debug = False)

    if show_list:
        pp(list = users_info.getInfo())

    if type(id_num) is not type(None):
        pp(list = users_info.queryById(id_num))
    else:
        print_command_help(Users)

# Create a command for keypair
@click.command()
@click.option('-l','--list','show_list',is_flag=True,help="Show list of keypairs")
@click.option('-id','id_num',is_flag = None,help="The user id")
def KeyPairs(show_list,id_num):
    '''
    Key to log in to VM
    '''
    key_info = keypairs('sys',debug = False)

    if show_list:
        pp(list = key_info.list())
    
    if type(id_num) is not type(None):
        pp(list = key_info.queryById(id_num))
    else:
        print_command_help(KeyPairs)

# Create a command for job
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help ="Show list of jobs")
@click.option('-id','id_num',is_flag = None,help="The user id")
def Jobs(show_list,id_num):
    """
    Batch job for K8s or Slurm
    """
    jobs_info = jobs('sys',debug = False)

    if show_list:
        pp(list = jobs_info.list())
    
    if type(id_num) is not type(None):
        pp(list = jobs_info.queryById(id_num))
    else:
        print_command_help(Jobs)

# Create a command for images
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of images")
@click.option('-id','id_num',is_flag = None,help="The user id")
def Images(show_list,id_num):
    '''
    Software configuration
    '''
    images_info = images('sys',debug = False)

    if show_list:
        pp(list = images.list())
    
    if type(id_num) is not type(None):
        pp(list = images_info.queryById(id_num))
    else:
        print_command_help(Images)

# Create a command for volumes
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of volumes")
@click.option('-id','id_num',is_flag = None,help="The user id")
def Volumes(show_list,id_num):
    """
    Attaching, detatching, extending disks for Openstack
    """
    volumes_info = volumes('sys',debug = False)

    if show_list:
        pp(list = volumes_info.list())
    
    if type(id_num) is not type(None):
        pp(list = volumes_info.queryById(id_num)) 
    else:
        print_command_help(Volumes)

# Create a command for snapshots
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of snapshots")
@click.option('-id','id_num',default = None,help="The user id")
def Snapshots(show_list,id_num):
    """
    Attaching, detatching, extending disks for Openstack
    """
    snapshots_info = snapshots('sys',debug = False)

    if show_list:
        pp(list = snapshots_info.list())
    
    if type(id_num) is not type(None):
        pp(list = snapshots_info.queryById(id_num))
    else:
        print_command_help(Snapshots)

# Create a command for buckets
@click.command()
@click.option('-l','--list','show_list',is_flag = True, help = "Show list of snapshots")
@click.option('-id','id_num', default = None, help = "The user id")
def Buckets(show_list,id_num):
    '''
    Storage space for Ceph
    '''
    buckets_info = buckets('sys',debug = False)

    if show_list:
        pp(list = buckets_info.list())
    
    if type(id_num) is not type(None):
        pp(list = buckets_info.queryById(id_num))
    else:
        print_command_help(Buckets)
    

# Add commands to cli command
cli.add_command(Acls)
cli.add_command(Users)
cli.add_command(KeyPairs)
cli.add_command(Jobs)
cli.add_command(Images)
cli.add_command(Volumes)
cli.add_command(Snapshots)
cli.add_command(Buckets)

def print_command_help(cmd):
    """
    Print the help command for the input function.
    """
    with click.Context(cmd) as ctx:
        click.echo(cmd.get_help(ctx))


def main():
    """
    this is a test main function
    """
    cli()

if __name__ == "__main__":
    main()
