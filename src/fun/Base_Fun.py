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
    @click.option('--group',is_flag = True, help = "Get all ACLs by api key")
    def list(group):
        acls_info = AclsFun.acls_auth()
        if group:
            print(acls_info.listGroup())
            #table_layout(' Acls Info ',acls_info.listGroup())
            pp(show_list = acls_info.listGroup())
        else:
            #pp(show_list = acls_info.list())
            print(type(acls_info.list()))
            #table_layout(' Acls Info ',acls_info.list(),acls_info.list().keys())
            pp(show_list = acls_info.list())
    Acls.add_command(list)

class ApiKeyFun():
    '''
   Funciton for API_Key CLI
    '''
    def __init__(self):
        pass

    @staticmethod
    def apikey_auth(auth='sys'):
        apikey_info = api_key(auth,debug = False)
        return apikey_info

    @click.group()
    def Api_Key():
        pass

    @click.command()
    @click.option('--describe',default = None, help = "Detail of specific keypair")
    def list(describe):
        apikey_info = ApiKeyFun.apikey_auth()
        if not isNone(describe):
            #table_layout(' API_key Info ',apikey_info.queryById(describe))
            print(type(apikey_info.queryById(describe)))
            pp(show_list = apikey_info.queryById(describe))
        else:
            #table_layout(' API_key Info ',apikey_info.list())
            print(type(apikey_info.list()))
            pp(show_list = apikey_info.list())
    Api_Key.add_command(list)

class KeyPairFun():
    '''
    Function for keypair CLI
    '''
    def __init__(self):
        pass

    @staticmethod
    def keypair_auth(auth='sys'):
        keypairs_info = keypairs(auth,debug = False)
        return keypairs_info

    @click.group()
    def Keypairs():
        pass

    @click.command()
    @click.option('--describe',default = None,help="Detail of specific keypair")
    def list(describe):
        key_info = KeyPairFun.keypair_auth()
        if not isNone(describe):
            #table_layout( ' {} Info '.format(describe),key_info.queryById(describe))
            pp(show_list = key_info.queryById(describe))
            pass
        else:
            pass
            pp(show_list = key_info.list())
            #table_layout(' KeyPairs Info ',key_info.list())

    @click.command()
    @click.option('-n','--name','info',default = None, help = "Create a new keypair")
    @click.pass_context
    def create_keypair(ctx,info):
        if not isNone(info):
            key_info = KeyPairFun.keypair_auth()
            pp(show_list = key_info.createKeyPair(info))
        else:
            print(ctx.get_help())

    @click.command()
    @click.option('-n','--name','info',default = None, help = "Delete a keypair")
    @click.pass_context
    def delete_keypair(ctx,info):
        if not isNone(info):
            key_info = KeyPairFun.keypair_auth()
            pp(show_list = key_info.delete(info))
        else:
            print(ctx.get_help())

    Keypairs.add_command(list)
    Keypairs.add_command(create_keypair)
    Keypairs.add_command(delete_keypair)

class ProjectFun():
    '''
   Funciton for Project CLI
    '''
    def __init__(self):
        pass

    @staticmethod
    def project_auth(auth='sys'):
        projects_info = projects(auth,debug = False)
        projects_info._csite_ = 'k8s-taichung-default'
        return projects_info

    @click.group()
    def Projects():
        pass

    @click.command()
    @click.option('--describe',default = None, help = "Detail of specific keypair")
    def list(describe):
        projects_info = ProjectFun.project_auth()
        if not isNone(describe):
            #table_layout(' Project Info ',projects_info.queryById(describe))
            pp(show_list = projects_info.queryById(describe))
            pass
        else:
            #table_layout(' Projects Info ',projects_info.list())
            pp(show_list = projects_info.list())
            pass
    Projects.add_command(list)

class UserFun():
    '''
   Funciton for User CLI
    '''
    def __init__(self):
        pass

    @staticmethod
    def user_auth(auth='sys'):
        user_info = users(auth,debug = False)
        return user_info

    @click.group()
    def Users():
        pass

    @click.command()
    @click.option('--describe',default = None, help = "Detail of specific keypair")
    def list(describe):
        user_info = UserFun.user_auth()
        if not isNone(describe):
            #table_layout(' User Info ',user_info.queryById(describe))
            pp(show_list = user_info.queryById(describe))
        else:
            #table_layout(' User Info ',user_info.list())
            pp(show_list = user_info.list())
            pass
    Users.add_command(list)


