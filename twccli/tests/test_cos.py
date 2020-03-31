# -*- coding: utf-8 -*-
from click.testing import CliRunner
#from ..twcc import Session2
#from ..twcc.util import isNone
import os
import re
import click
import json
from ..twccli import cli
import pytest
import uuid
import subprocess

class TestCosLifecyc:

    def _loadSession(self):
        self.runner = CliRunner()

    def _loadParams(self):
        self.bk_name = "bk_{}".format(str(uuid.uuid1()).split("-")[0])
        self.dir = "dir_{}".format(str(uuid.uuid1()).split("-")[0])

    def __run(self, cmd_list):
        result = self.runner.invoke(cli, cmd_list)
        #print(result.output)
        print(result)
        #assert result.exit_code == 0
        return result.output

    def _create_bucket(self, bk):
        cmd_list = "mk cos -n {}".format(bk)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))  

    def _list_bucket_after_create(self):
        cmd_list = "ls cos -json"
        print(cmd_list)
        self.list_out = self.__run(cmd_list.split(u" "))  
        print(self.list_out)
        out = json.loads(self.list_out)
        
        flag = False
        for ele in out:
            if ele['Name'] == self.bk_name:
                flag = True

        assert flag

    def _del_bucket(self, bkt):
        cmd_list = "rm cos -n {} -f -r".format(bkt)
        print(cmd_list)
        out = self.__run(cmd_list.split(u" "))  


    def _list_bucket_after_delete(self):
        cmd_list = "ls cos -json"
        print(cmd_list)
        self.list_out = self.__run(cmd_list.split(u" "))  
        out = json.loads(self.list_out)
        
        flag = True
        for ele in out:
            if ele['Name'] == self.bk_name:
                flag = False

        assert flag

    def _upload_files(self):
        cmd_list = "cp cos -upload -src {} -dest {} -r".format(self.upload_dir, self.bk_name)
        print(cmd_list)
        out = self.__run(cmd_list.split(u" "))  
        assert False

    def test_create_bucket(self):
        self._loadSession()
        self._loadParams()
        self._create_bucket(self.bk_name)
        self._list_bucket_after_create()
        self._del_bucket(self.bk_name)
        self._list_bucket_after_delete()

    def _create_hierarchy_files(self, dir):
        cmd1 = ["mkdir", dir]
        cmd2 = ["touch", dir + "/1.txt", dir + "/2.txt"]
        cmd3 = ["mkdir", dir + "/subdir"]
        cmd4 = ["touch", dir + "/subdir/3.txt", dir + "/subdir/4.txt"]

        p = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        p.communicate()
        p = subprocess.Popen(cmd2, stdout=subprocess.PIPE)
        p.communicate()        
        p = subprocess.Popen(cmd3, stdout=subprocess.PIPE)
        p.communicate()
        p = subprocess.Popen(cmd4, stdout=subprocess.PIPE)
        p.communicate()


    def _upload_files(self, bk, dir):
        cmd_list = "cp cos -upload -src {} -dest {} -r".format(dir, bk)
        print(cmd_list)
        out = self.__run(cmd_list.split(u" "))  

    def _del_isu85_files(self):
        dir = self.isu85_Dir.replace("./", "")
        cmd = ["rm", "-rf", self.isu85_Dir]
        subprocess.run(cmd)

    def _check_isu85_upload_files(self):
        '''
        localList = []
        for localF in out.splitlines():
            localList.append(localF)
            print('local {}'.format(localF))
        '''

        # ================
        
        cmd_remote = "ls cos -n {} -json".format("bk123")
        print(cmd_remote)
        self.list_out = self.__run(cmd_remote.split(u" "))  
        out2 = json.loads(self.list_out)
        print(out2)
        


        #flag = True
        remoteList = []
        for ele in out2:
            str = ele['Key']
            remoteList.append(str)
            print('remote = {}'.format(str))
 
        for root, dirs, files in os.walk('./updir'):
            for name in files:
                print("file={}".format(os.path.join(root, name)))
                scanPath = os.path.join(root, name)
                scanPath = scanPath.replace('./','')
                if scanPath in remoteList :
                    print('yes {}'.format(scanPath))
                else:
                    print('no {}'.format(scanPath))


        assert False


    
    def test_issue_85(self):
        bk_isu85 = "bk_isu85_{}".format(str(uuid.uuid1()).split("-")[0])
        isu85_Dir = "./isu85_{}".format(str(uuid.uuid1()).split("-")[0])
        
        self._loadSession()
        self._create_bucket(bk_isu85)

        self._create_hierarchy_files(isu85_Dir)
        self._upload_files(bk_isu85, isu85_Dir)
        self._del_bucket(bk_isu85)



    def test_issue_78(self):

        bk_isu78 = "bk_isu78_{}".format(str(uuid.uuid1()).split("-")[0])
        isu78_Dir = "./isu78_{}".format(str(uuid.uuid1()).split("-")[0])

        self._loadSession()

        self._create_bucket(bk_isu78)
        self._create_hierarchy_files(isu78_Dir)
        self._upload_files(bk_isu78, isu78_Dir)
        self._del_bucket(bk_isu78)

    