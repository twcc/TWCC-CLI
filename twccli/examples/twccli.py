from __future__ import print_function

import sys, os
import click
import re
from twcc.services.s3_tools import S3
from twcc.services.solutions import solutions
from twcc.util import pp, table_layout, SpinCursor
from twcc.services.compute import sites
from twcc.services.base import acls, users, image_commit
from twcc.session import session_start
from prompt_toolkit.shortcuts import get_input
from twcc.services.projects import projects
from twcc.services.base import acls,users,keypairs,projects,api_key
from fun.Base_Fun import AclsFun,KeyPairFun
from twcc.services.storage import images,volumes,snapshots,buckets
import time
#====== Aug Old Code =======
def doSiteReady(site_id):
    b = sites(debug=False)
    wait_ready = False
    while not wait_ready:
        print("Waiting for container to be Ready.")
        if b.isReady(site_id):
            wait_ready = True
        time.sleep(5)
    return site_id

def Snapshots(show_list,id_num):

    snapshots_info = snapshots('sys',debug = False)
    if show_list:
        pp(list = snapshots_info.list())
    elif type(id_num) is not type(None):
        pp(list = snapshots_info.queryById(id_num))


def list_all_img():
  print("Note : this operation take 1-2 mins")
  a = solutions()
  cntrs = [(cntr['name'], cntr['id']) for cntr in a.list() if not cntr['id'] in block_set]
  sol_list = sites.getSolList(name_only=True)
  base_site = sites(debug=False)
  output = []
  for (sol_name, sol_id) in cntrs:
    output.append({"sol_name": sol_name,
            "sol_id": sol_id,
            "images" : base_site.getAvblImg(sol_id, sol_name)})


  table_layout("img", output, ['sol_name', 'sol_id', 'images'])


def list_buckets():
  s3 = S3()
  buckets = s3.list_bucket()
  s3.test_table(buckets)

def list_files(bucket_name):
  s3 = S3()
  files = s3.list_object(bucket_name)
  s3.test_table(files)


def list_all_solution():
  a = solutions()
  cntrs = a.list()
  col_name = ['id','name', 'create_time']
  table_layout("all avaliable solutions", cntrs, caption_row = col_name)

def list_sol():
  list_all_solution()
  print(sites.getSolList(mtype='list', name_only = True))

def list_cntr(site_id, isTable,isAll):

    if not type(site_id)==type(1):
        raise ValueError("Site number: '{0}' error.".format(site_id))

    if not isTable:
        gen_cntr(site_id)
    else:
        a = sites()
        if type(a.list(isAll=isAll)) is dict and 'detail' in a.list(isAll=isAll).keys():
            isAll = False
        if site_id==0:
            my_sites = a.list(isAll=isAll)
            if len(my_sites)>0:
                col_name = ['id','name', 'create_time', 'status']
                table_layout('sites', my_sites, caption_row=col_name)
        else:
            res = a.queryById(site_id)
            col_name = ['id','name', 'create_time', 'status', 'status_reason']
            table_layout('sites: %s'%site_id, res, caption_row=col_name)

def list_commit():
    print('list commit')
    c = image_commit()
    print(c.getCommitList())

def list_project():
    proj = projects()
    for cluster in proj.getSites():
        proj._csite_ = cluster
        print ("="*5, cluster, "="*5)
        table_layout ("Proj for {0}".format(cluster), proj.list(), ['id', 'name'])

def create_bucket(bucket_name):
  s3 = S3()
  s3.create_bucket(bucket_name)

def del_bucket(bucket_name,df):
  s3 = S3()
  s3.del_bucket(bucket_name,df)

#===== create =======

def create_cntr(cntr_name, gpu, sol_name, sol_img, isWait):
    def_header = sites.getGpuDefaultHeader(gpu)
    a = solutions()
    cntrs = dict([(cntr['name'], cntr['id']) for cntr in a.list() if not cntr['id'] in block_set and cntr['name']==sol_name])
    if len(cntrs)>0:
        sol_id = cntrs[sol_name]
    else:
      raise ValueError("Solution name '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    b = sites(debug=False)
    imgs = b.getAvblImg(sol_id, sol_name, latest_first=True)
    if type(sol_img) == type(None) or len(sol_name)==0:
      def_header['x-extra-property-image'] = imgs[0]
    else:
        if sol_img in imgs:
          def_header['x-extra-property-image'] = sol_img
        else:
          raise ValueError("Container image '{0}' for '{1}' is not valid.".format(sol_img, sol_name))

    res = b.create(cntr_name, sol_id, def_header)
    if 'id' not in res.keys():
        if 'message' in res:
            raise ValueError("Can't find id, please check error message : {}".format(res['message']))
        if 'detail' in res:
            raise ValueError("Can't find id, please check error message : {}".format(res['detail']))
    else:
        print("Site id: {0} is created.".format(res['id']))

    if isWait:
        doSiteReady(res['id'])
    return int(res['id'])

# remove ===========================
def del_cntr(con_ids):
    a = sites()
    if type(con_ids) == type(1):
        con_ids = [con_ids]
    if len(list(con_ids)) > 0:
        for con_id in con_ids:
            a.delete(con_id)
            print("Successfully remove {}".format(con_id))
    else:
        print("Need to enter Container ID")
#=== bind_port / unbind_port =====

def gen_cntr(s_id):
    print("This is container information for connection. ")
    b = sites()
    site_id = s_id
    conn_info = b.getConnInfo(site_id)
    print (conn_info)


def list_port(site_id):
  b = sites()
  conn_info = b.getConnInfo(site_id)

#== upload/download ========
def upload(source,directory,key,r):
  s3 = S3()
  # Check for source type
  if os.path.isdir(source):
    if r != True:
      print('r != True, directory') 
      raise Exception("{} is path, need to set recursive to True".format(source))
    else:
      print('dir upload')
      s3.upload_bucket(path = source ,bucket_name = directory,r=r)
  else:
    
    if key == None:
        key = source.split('/')[-1]
    
    s3.upload_bucket(file_name = source ,bucket_name = directory,key = key)

def download(source,directory,key,r):
  print('enter download')
  s3 = S3() 
  if not s3.check_4_bucket(source):
    raise Exception("No such bucket name {} exists".format(source)) 

  if os.path.isdir(directory) and key == None:
    print('is dir')
    if r != True:
      raise Exception("{} is path, need to set recursive to True".format(directory))
    else:
      s3.download_bucket(bucket_name = source,path=directory,r=r)
  else:
    print('is file')
    if key.endswith('*'):
      files = s3.list_object(source)
      prefix_folder = '/'.join(key.split('/')[:-1])
      desire_files = s3.list_files_v2(bucket_name=source,delimiter='',prefix=prefix_folder)
      for desire_file in desire_files:
        if not desire_file.endswith('/'):
          print('desire_file = '+desire_file) 
          new_directory = directory + desire_file
          s3.download_bucket(file_name = new_directory,bucket_name = source,key = desire_file)
    else:

      if directory.endswith('/'):
        directory = directory + key      

      print('directory ='+ directory)
      s3.download_bucket(file_name = directory,bucket_name = source,key = key)

    print('download end')
#===========================

@click.command()
@click.option('-c', 'res_type', flag_value='Container',
              default=True)
@click.option('-o', 'res_type', flag_value='Cos')
@click.option('-v', 'res_type', flag_value='Vcs')
@click.option('-n', 'res_type', flag_value='Network')
@click.option('-k', 'res_type', flag_value='Keypair')
@click.argument('id', nargs=-1)
@click.option('-name','--name','name', help = 'Name of the Bucket.')
@click.option('-r','r', is_flag = True,help = 'Help delete all the files inside the bucket before delete bucket.')


def rm(res_type, id, name, r):

  if res_type == 'Container':
    if not id:
      print('res_types {} ,con id empty'.format(id))
    else:
      del_cntr(id)
  elif res_type == 'Cos':
    print('enter cos')
    if not name:
      print('please enter bucket_name')
    else:
      print('enter remove bucket name')
      del_bucket(name, r)

@click.command()
@click.option('-c', 'res_type', flag_value='Container',
              default=True)
@click.option('-o', 'res_type', flag_value='Cos')
@click.option('-v', 'res_type', flag_value='Vcs')
@click.option('-n', 'res_type', flag_value='Network')
@click.option('-k', 'res_type', flag_value='Keypair')
@click.option('-p', 'res_type', flag_value='Port')

@click.option('-img', 'res_property', flag_value='image')
@click.option('-vol', 'res_property', flag_value='volumne')
@click.option('-sol', 'res_property', flag_value='solution')
@click.option('-hfs', 'res_property', flag_value='HFS Service')
@click.option('-commit', 'res_property', flag_value='commit')

@click.option('-site',  'site_id', default = 0, type = int, help="Enter the site id")
@click.option('-table', 'is_table', default = True, type = bool, help="Show cntr info in table style.")
@click.option('-all',   'is_all', is_flag = True, type = bool, help="Show all container.")
@click.option('-name',  'name',  type = str, help = "Enter name")
@click.option('-id','id_num',default = None, help = "The API key id")


def ls(res_type, res_property, site_id, is_table, is_all
       , id_num, name):

  if res_type == 'Cos':
    if not name:
      list_buckets()
    else:
      list_files(name)

    return True

  if res_type == 'Port':
     list_port(site_id)

  if res_type == 'Container':
    if res_property == 'solution':
      list_sol()

    if res_property == 'image':
        print('list all image')
        list_all_img()
    if res_property == 'commit':
       list_commit()

    if not res_property:
      list_cntr(site_id, is_table, is_all)

    return True

  if res_type == 'Vcs':
    if res_property == 'solution':
      list_sol()
      return True

    if res_property == 'Cos':

      if not name:
        list_buckets()
        return True
      else:
        print('has bucket name value')
        list_files(name)
        return True

  return False

@click.command()
@click.option('-c', 'res_type', flag_value='Container',
              default=True)

@click.option('-snapshot', 'res_property', flag_value='snapshot')
@click.option('-l','--list','show_list',is_flag = True,help = "Show list of snapshots")
@click.option('-id','id_num',default = None,help="The snapshot id")

def mv(res_type, res_property, show_list, id_num):
  Snapshots(show_list,id_num)

@click.command()
@click.option('-upload','op', flag_value='upload')
@click.option('-download','op', flag_value='download')

@click.option('-s','--source','source',required=True, help = 'Name of the File.')
@click.option('-d','--directory','directory',required=True, help = 'Name of the Bucket.')
@click.option('-k','--key','key',help ='The name of the key to upload to.') 
@click.option('-r','r',is_flag = True,help = 'Recursively copy entire directories.' )
def cp(op, source, directory, key, r):
  if op == 'upload':
    print('enter upload')
    upload(source, directory, key, r= r)
  if op == 'download':
    print('enter download')
    download( source, directory, key, r=r)   

@click.command()
@click.option('-c', 'res_type', flag_value='Container',
              default=True)
@click.option('-o', 'res_type', flag_value='Cos')
@click.option('-v', 'res_type', flag_value='Vcs')
@click.option('-n', 'res_type', flag_value='Network')
@click.option('-k', 'res_type', flag_value='Keypair')

@click.option('-name',     'name', default = "twcc-cli", type = str, help = "Enter name")
@click.option('-gpu',      'gpu',default = 1, type = int, help = "Enter number of gpu")
@click.option('-sol',      'sol', default = "TensorFlow", type = str, help = "Enter solution name")
@click.option('-img_name', 'img_name', default = None, type = str, help = "Enter image name")
@click.option('-wait',     'wait', default = True, type = bool,  help = "Need to wait for cntr")

def mk(res_type, name, gpu, sol, img_name, wait):

  if res_type == 'Container':
    create_cntr(name, gpu, sol, img_name, wait)
    print('create_cntr')
    return True

  if res_type == 'Cos':
    create_bucket(name)
    return True

  return False

@click.command()
@click.option('-u', '--op', flag_value='unbind')
@click.option('-p','port', type = int , help ='number of port') 
@click.option('-site','siteId',type = int ,help ='site id') 
def bind(op, port, siteId):
  b = sites()
  if not op: 
    print('bind')
    b.exposedPort(siteId, port)
  else:
    b.unbindPort(siteId, port)
    print(siteId, port) 
    #b.getConnInfo(siteId)

@click.group()
def cli():
  print('enter cli')
  pass

cli.add_command(mk)
cli.add_command(rm)
cli.add_command(ls)
cli.add_command(mv)
cli.add_command(cp)
cli.add_command(bind)

if __name__ == "__main__":
    cli()
