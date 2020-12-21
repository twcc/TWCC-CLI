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


class TestVcsLifecyc:
    def _loadParams(self):
        self.key_name = "twccli_{}".format(str(uuid.uuid1()).split("-")[0])
        (self.flv, self.sol, self.img, self.sys_vol) =  ("v.super", "ubuntu", "Ubuntu 20.04", "local")
        self.ext_port = "81"
        self.ext_port_range = "3000-3010"
        self.apikey = os.environ['TWCC_API_KEY']
        self.pcode = os.environ['TWCC_PROJ_CODE']

    def _loadSession(self):
        self.runner = CliRunner()

    def __run(self, cmd_list):
        return self.__exec_run(cmd_list, 0)

    def __exec_run(self, cmd_list, expected=0):
        result = self.runner.invoke(cli, cmd_list)

        print(result.output)
        print(result)
        assert result.exit_code == expected
        return result.output

    def __runError(self, cmd_list):
        return self.__exec_run(cmd_list, 1)

    def _create_key(self):
        cmd_list = "mk key --name {}".format(self.key_name)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def _list_key(self):
        cmd_list = "ls key -n {} -json".format(self.key_name)
        self.list_out = self.__run(cmd_list.split(" "))
        print(self.list_out)

    def _delete_key(self):
        cmd_list = "rm key --force {}".format(self.key_name)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)
    def _create_vlb(self):
        cmd_list = "mk vlb --load_balance_name {} -wait -json".format('twccli_vlb')
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)
        self.vlb_id = json.loads(out)['id']

    def _add_member_vlb(self):
        cmd_list = "ch vlb --member {} {} -id {}".format('192.168.10.10:8080','192.168.11.11:9090',self.vlb_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _delete_vlb(self):
        cmd_list = "rm vlb -id {} --force".format(self.vlb_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)

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

    def _list_vcs(self):
        cmd_list = "ls vcs -json {}".format(self.vcs_id)
        self.list_out = self.__run(cmd_list.split(" "))
        print(self.list_out)

    def _stop_vcs(self):
        cmd_list = "ch vcs -s {} -sts Stop -wait".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _start_vcs(self):
        cmd_list = "ch vcs -s {} -sts Ready -wait".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _del_vcs(self):
        cmd_list = "rm vcs --force {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg(self):
        cmd_list = "net vcs -p {} -s {}".format(self.ext_port, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg_range(self):
        cmd_list = "net vcs -prange {} -s {}".format(self.ext_port_range, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg_range_and_port(self):
        cmd_list = "net vcs -prange {} -p {} -s {}".format(self.ext_port_range,
                self.ext_port, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg_without_range_and_port(self):
        cmd_list = "net vcs -s {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__runError(cmd_list.split(" "))

    def _list_secg(self):
        cmd_list = "ls vcs -secg -json {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        jobj = json.loads(out)
        for ele in jobj:
            if not isNone(ele['port_range_min']):
                if int(self.ext_port) == int(ele['port_range_min']):
                    self.secg_id = ele['id']
                    return True
        raise Exception("Error, can not find port {}".format(self.ext_port))

    def _del_secg(self):
        cmd_list = "rm vcs -secg --force {} --site-id {}".format(self.secg_id, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)
    

    def test_vlb(self):
        self._loadParams()
        self._loadSession()
        self._create_vlb()
        self._add_member_vlb()
        import time
        time.sleep(120)
        self._delete_vlb()

    def test_lifecycle(self):
        self._loadParams()
        self._loadSession()
        self._create_key()
        self._list_key()
        self._create_vcs()
        self._add_secg_range()
        self._add_secg_range_and_port()
        self._add_secg_without_range_and_port()
        self._list_vcs()
        self._stop_vcs()
        self._start_vcs()
        self._add_secg()
        self._list_secg()
        self._del_secg()
        self._del_vcs()
        self._delete_key()
