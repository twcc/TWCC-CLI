# -*- coding: utf-8 -*-
from click.testing import CliRunner
from ..twcc import Session2
from ..twcc.util import isNone
from ..twccli import cli
import os
import re
import click
import json
import pytest
import uuid

class TestVcsPort:
    def _loadParams(self):
        self.key_name = "twccli_{}".format(str(uuid.uuid1()).split("-")[0])
        (self.flv, self.sol, self.img, self.sys_vol) =  ("v.super", "ubuntu", "Ubuntu 16.04", "local")
        self.ext_port_range = "3000-3010"
        self.ext_port = "8080"
        self.apikey = os.environ['TWCC_API_KEY']
        self.pcode = os.environ['TWCC_PROJ_CODE']

    def _loadSession(self):
        self.runner = CliRunner()

    def __run(self, cmd_list):
        return self.__exec_run(cmd_list)


    def __runError(self, cmd_list):
        return self.__exec_run(cmd_list, 1)

    def __exec_run(self, cmd_list, expected=0):
        result = self.runner.invoke(cli, cmd_list)

        print(result.output)
        print(result)
        assert result.exit_code == expected
        return result.output


    def _create_key(self):
        cmd_list = "mk key --name {}".format(self.key_name)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def _create_vcs(self):
        paras = ["mk", "vcs",
                "--name",           self.key_name,
                "--image-type-name",self.sol,
                "--product-type",   self.flv,
                "--img_name",       self.img,
                "--keypair",        self.key_name,
                "--system-volume-type", self.sys_vol,
                "--data-volume-type", "ssd-encrypt",
                "--data-volume-size", "1",
                "-wait", "-json"
                ]
        print(" ".join(paras))
        out = self.__run(paras)
        self.vcs_id = json.loads(out)['id']

    def _add_secg_range(self):
        cmd_list = "net vcs -secg -prange {} -s {}".format(self.ext_port_range, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg_range_and_port(self):
        cmd_list = "net vcs -secg -prange {} -p {} -s {}".format(self.ext_port_range,
                self.ext_port, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg_without_range_and_port(self):
        cmd_list = "net vcs -secg -s {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__runError(cmd_list.split(" "))

    def _list_secg(self):
        cmd_list = "ls vcs -secg -json {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        jobj = json.loads(out)
        for ele in jobj:
            if not isNone(ele['port_range_min']):
                if int(self.ext_port_range.split('-')[0]) == int(ele['port_range_min']) and int(self.ext_port_range.split('-')[1]) == int(ele['port_range_max']):
                    self.secg_id = ele['id']
                    return True
        raise Exception("Error, can not find port {}".format(self.ext_port_range))

    def _del_secg(self):
        cmd_list = "rm vcs -secg --force {} --site-id {}".format(self.secg_id, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)

    def _del_vcs(self):
        cmd_list = "rm vcs --force {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _delete_key(self):
        cmd_list = "rm key --force {}".format(self.key_name)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)

    def test_lifecycle(self):
        self._loadParams()
        self._loadSession()
        self._create_key()
        self._create_vcs()
        self._add_secg_range()
        self._add_secg_range_and_port()
        self._add_secg_without_range_and_port()
        self._list_secg()
        self._del_secg()
        self._del_vcs()
        self._delete_key()
