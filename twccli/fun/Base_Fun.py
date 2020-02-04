from __future__ import print_function
from twcc.services.base import acls,api_key,keypairs,projects,users
from twcc.util import pp,isNone,table_layout

import click

class AclsFun():
    '''
    Funciton for Acls CLI
    '''
    def __init__(self):
        pass
    
    @staticmethod
    def acls_auth(auth='sys'):
        acls_info = acls(auth,debug = False)
        return acls_info
    
    @click.group()
    def Acls():
        pass
    
    @click.command()
    @click.option('--describe',default = None, help = "Detail of specific keypair")
    def list(describe):
        acls_info = AclsFun.acls_auth()
        if not isNone(describe):
            table_layout(' Acls Info ',acls_info.queryById(describe))
        else:
            pp(show_list = acls_info.list())
            #table_layout(' Acls Info ',acls_info.list()) 
    Acls.add_command(list)

class KeyPairFun():
    '''
    Function for keypair CLI
    '''
    def __init__(self):
        pass

    @staticmethod
    def keypair_data_info(auth='sys'):
        keypairs_info = keypairs(auth,debug = False)
        return keypairs_info
        
    @click.group()
    def Keypairs():
        pass
    
    @click.command()
    @click.option('--describe',default = None,help="Detail of specific keypair")
    def list(describe):
        key_info = KeyPairFun.keypair_data_info()
        if not isNone(describe):
            table_layout( ' {} Info '.format(describe),key_info.queryById(describe))
        else:
            #pp(show_list = key_info.list())
            table_layout(' KeyPairs Info ',key_info.list())
    
    @click.command()
    @click.option('-n','--name','info',default = None, help = "Create a new keypair")
    @click.pass_context
    def create_keypair(ctx,info):
        if not isNone(info):
            key_info = KeyPairFun.keypair_data_info()
            pp(show_list = key_info.createKeyPair(info))
        else:
            print(ctx.get_help())

    @click.command()
    @click.option('-n','--name','info',default = None, help = "Delete a keypair")
    @click.pass_context
    def delete_keypair(ctx,info):
        if not isNone(info):
            key_info = KeyPairFun.keypair_data_info()
            pp(show_list = key_info.delete(info))
        else:
            print(ctx.get_help())

    Keypairs.add_command(list)
    Keypairs.add_command(create_keypair)
    Keypairs.add_command(delete_keypair)
