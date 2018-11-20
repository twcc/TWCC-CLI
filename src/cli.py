#-*- coding: utf-8 -*-
from __future__ import print_function
"""NCHC TWCC-CLI command line tool

.. module:: twcc-cli
   :synopsis: A useful module indeed.
.. moduleauthor:: August Chao <1803001@narlabs.org.tw>
"""
from twcc.services.base import acls,users,keypairs
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
def Acls(show_list):
    '''
    Access control of IaaS
    '''
    if show_list == 'list':
        acls_list = acls('sys')
        pp(list=acls_list.getSites())
    elif show_list == 'list_g':
        acls_list = acls('sys')
        pp(list=acls_list.listGroup())
    else:
        print("Please choose --list to show list of the current acls")
        print("Or")
        print("Please choose --list_g to show list of the current acls_group")
   
# Create a command for users 
@click.command()
@click.option('-l','--list','show_list',is_flag=True,help="Show list of users")
def Users(show_list):
    '''
    Show user's information
    '''
    if show_list:
        users_list = users('sys')
        pp(list = users_list.getInfo())
    else:
        print("Please enter -l or --list to show the list of the users")   

# Create a command for keypair
@click.command()
@click.option('-l','--list','show_list',is_flag=True,help="Show list of keypairs")
def KeyPairs(show_list):
    '''
    Show list of keypairs
    '''
    if show_list:
        key_list = keypairs('sys')
        pp(list = key_list.list())
    else:
        print("Please enter -l or --list to show the list of the keypairs")

# Create a command for job
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help ="Show list of jobs")
def Jobs(show_list):
    """
    Show list of jobs
    """
    if show_list:
        jobs_list = jobs('sys')
        pp(list = jobs_list.list())
    else:
        print("Please enter -l or --list to show the list of the jobs")

# Create a command for images
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of images")
def Images(show_list):
    '''
    Show list of images
    '''
    if show_list:
        images_list = images('sys')
        pp(list = images.list())
    else:
        print("Please enter -l or --list to show the list of images")

# Create a command for volumes
@click.command()
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of volumes")
def Volumes(show_list):
    """
    Show list of volumes
    """
    if show_list:
        volumes_list = images('sys')
        pp(list = images.list())
    else:
        print("Please enter -l or --list to show the list of volumes")

# Add commands to cli command
cli.add_command(Acls)
cli.add_command(Users)
cli.add_command(KeyPairs)
cli.add_command(Jobs)
cli.add_command(Images)
def main():
    """
    this is a test main function
    """
    cli()

if __name__ == "__main__":
    main()
