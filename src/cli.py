#-*- coding: utf-8 -*-
from __future__ import print_function
"""NCHC TWCC-CLI command line tool

.. module:: twcc-cli
   :synopsis: A useful module indeed.
.. moduleauthor:: August Chao <1803001@narlabs.org.tw>
"""
#from twcc.twcc import TWCC
#from twcc.services.base import acls,users,keypairs
from twcc.services.base import acls as ACLS
from twcc.util import pp

import click

# Create groups for command
@click.group()
def cli():
    pass

# Create a function for acls
@click.command()
@click.option('--list','show_list',flag_value='list',help='Show the list of acls')
@click.option('--list_g','show_list',flag_value='list_g',help='Show the list of acls_g')
def acls(show_list):
    '''
    Access control of IaaS
    '''
    if show_list == 'list':
        a = ACLS('sys')
        pp(list=a.list())
    elif show_list == 'list_g':
        a = ACLS('sys')
        pp(list=a.listGroup())
    else:
        print("Please choose --list to show list of the current acls")
        print("Or")
        print("Please choose --list_g to show list of the current acls_group")
   

cli.add_command(acls)

def main():
    """
    this is a test main function
    """
    cli()

if __name__ == "__main__":
    main()
