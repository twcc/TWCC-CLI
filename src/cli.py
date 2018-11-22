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
from twcc.util import pp,isNone
from fun.Base_Fun import AclsFun,KeyPairFun 
import click

# Create groups for command
@click.group()
def cli():
    pass

# Create a command for users 
@click.command()
@click.option('-l','--list','show_list',is_flag=True,help="Show list of users")
@click.option('-id','id_num',is_flag = None,help="The user id")
def Users(show_list,id_num):
    '''
    '''
    users_info = users('sys',debug = False)

    if show_list:
        pp(list = users_info.getInfo())
    elif type(id_num) is not type(None):
        pp(list = users_info.queryById(id_num))
    else:
        printCommandHelp(Users)

# Create a command for job
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help ="Show list of jobs")
@click.option('-id','id_num',is_flag = None,help="The job id")
def Jobs(show_list,id_num):
    """
    """
    jobs_info = jobs('sys',debug = False)

    if show_list:
        pp(list = jobs_info.list())
    elif type(id_num) is not type(None):
        pp(list = jobs_info.queryById(id_num))
    else:
        printCommandHelp(Jobs)

# Create a command for images
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of images")
@click.option('-id','id_num',is_flag = None,help="The image id")
def Images(show_list,id_num):
    '''
    '''
    images_info = images('sys',debug = False)

    if show_list:
        pp(list = images.list())
    elif type(id_num) is not type(None):
        pp(list = images_info.queryById(id_num))
    else:
        printCommandHelp(Images)

# Create a command for volumes
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of volumes")
@click.option('-id','id_num',is_flag = None,help="The volume id")
def Volumes(show_list,id_num):
    """
    """
    volumes_info = volumes('sys',debug = False)

    if show_list:
        pp(list = volumes_info.list())
    elif type(id_num) is not type(None):
        pp(list = volumes_info.queryById(id_num)) 
    else:
        printCommandHelp(Volumes)

# Create a command for snapshots
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of snapshots")
@click.option('-id','id_num',default = None,help="The snapshot id")
def Snapshots(show_list,id_num):
    """
    """
    snapshots_info = snapshots('sys',debug = False)

    if show_list:
        pp(list = snapshots_info.list())
    elif type(id_num) is not type(None):
        pp(list = snapshots_info.queryById(id_num))
    else:
        printCommandHelp(Snapshots)

# Create a command for buckets
@click.command()
@click.option('-l','--list','show_list',is_flag = True, help = "Show list of buckets")
@click.option('-id','id_num', default = None, help = "The bucket id")
def Buckets(show_list,id_num):
    '''
    '''
    buckets_info = buckets('sys',debug = False)

    if show_list:
        pp(list = buckets_info.list())
    elif type(id_num) is not type(None):
        pp(list = buckets_info.queryById(id_num))
    else:
        printCommandHelp(Buckets)

# Create a command for projects
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of projects ")
@click.option('-id','id_num',default = None, help = "The project id")
def Projects(show_list,id_num):
    '''
    '''
    projects_info = projects('sys',debug = False)
    
    if show_list:
        pp(list = projects_info.list())
    elif type(id_num) is not type(None):
        pp(list = projects_info.queryById(id_num))
    else:
        printCommandHelp(Projects)    

# Create a command for api_key
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of API_keys")
@click.option('-id','id_num',default = None, help = "The API key id")
def Api_Key(show_list,id_num):
    '''
    '''
    api_info = api_key('sys',debug = False)

    if show_list:
        pp(list = api_info.list())
    elif type(id_num) is not type(None):
        pp(list = api_info.queryById(id_num))
    else:
        printCommandHelp(Api_Key)

ac = AclsFun()
kp = KeyPairFun()

# Add commands to cli command
#cli.add_command(Acls)
cli.add_command(ac.Acls)
cli.add_command(Users)
cli.add_command(kp.Keypairs)
cli.add_command(Jobs)
cli.add_command(Images)
cli.add_command(Volumes)
cli.add_command(Snapshots)
cli.add_command(Buckets)
cli.add_command(Projects)
cli.add_command(Api_Key)

def printCommandHelp(cmd):
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
