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


class TestCosLifecyc:

    def _loadSession(self):
        self.runner = CliRunner()

    def _loadParams(self):
        self.bk_name = "bk_{}".format(str(uuid.uuid1()).split("-")[0])
        #self.up_file = "upFile_{}.txt".format(str(uuid.uuid1()).split("-")[0])
        print('bk_name= ' , self.bk_name)

    def __run(self, cmd_list):
        result = self.runner.invoke(cli, cmd_list)
        #print(result.output)
        print(result)
        #assert result.exit_code == 0
        return result.output

    def _create_bucket(self):
        cmd_list = "mk cos -n {}".format(self.bk_name)
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

    def _del_bucket(self):
        cmd_list = "rm cos {} -f".format(self.bk_name)
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

    def test_create_bucket(self):
        self._loadSession()
        self._loadParams()
        self._create_bucket()
        self._list_bucket_after_create()
        self._del_bucket()
        self._list_bucket_after_delete()