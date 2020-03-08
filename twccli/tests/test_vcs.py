# -*- coding: utf-8 -*-
from click.testing import CliRunner
from twcc import _TWCC_SESSION_, Session2
from twcc.util import isNone
import re
import click
import json
from examples.twccli import cli
import pytest
import uuid


class TestVcsLifecyc:
    def _loadParams(self):
        self.key_name = "twccli_{}".format(str(uuid.uuid1()).split("-")[0])
        (self.flv, self.sol, self.img, self.sys_vol) =  ("v.super", "ubuntu", "Ubuntu 16.04", "local")
        self.ext_port = "81"

    def _loadSession(self):
        mySession = Session2()
        self.runner = CliRunner()
        assert mySession.getApiKey() == Session2._getApiKey()

    def __run(self, cmd_list):
        result = self.runner.invoke(cli, cmd_list)

        print(result.output)
        print(result)
        assert result.exit_code == 0
        return result.output

    def _create_key(self):
        cmd_list = "mk vcs -key --name {}".format(self.key_name)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def _list_key(self):
        cmd_list = "ls -key {}".format(self.key_name)
        self.list_out = self.__run(cmd_list.split(" "))
        print(self.list_out)

    def _delete_key(self):
        cmd_list = "rm -key --force {}".format(self.key_name)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)

    def _create_vcs(self):
        paras = ["mk", "-v",
                "--name",           self.key_name,
                "--sol",            self.sol,
                "--flavor-name",    self.flv,
                "--img_name",       self.img,
                "--keypair",        self.key_name,
                "--system-volume-type", self.sys_vol,
                "--wait",
                ]
        out = self.__run(paras)
        for mstr in out.split("\n"):
            if re.search("Waiting for resource:", mstr):
                self.vcs_id = mstr.split(" ")[3]
                return True

    def _list_vcs(self):
        cmd_list = "ls -v --json {}".format(self.vcs_id)
        self.list_out = self.__run(cmd_list.split(" "))
        print(self.list_out)

    def _del_vcs(self):
        cmd_list = "rm -v --force {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _add_secg(self):
        cmd_list = "net -secg -p {} {}".format(self.ext_port, self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _list_secg(self):
        cmd_list = "ls -v -secg --json {}".format(self.vcs_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        json_str = "[    {" + out.replace("\n", "").split("[    {")[1]
        jobj = json.loads(json_str)
        for ele in jobj:
            if not isNone(ele['port_range_min']):
                if int(self.ext_port) == int(ele['port_range_min']):
                    self.secg_id = ele['id']
                    return True
        raise Exception("Error, can not find port {}".format(self.ext_port))

    def _del_secg(self):
        cmd_list = "rm -secg --force {}".format(self.secg_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))
        print(out)


    def test_lifecycle(self):
        self._loadParams()
        self._loadSession()
        self._create_key()
        self._list_key()
        self._create_vcs()
        self._list_vcs()
        self._add_secg()
        self._list_secg()
        self._del_secg()
        self._del_vcs()
        self._delete_key()

#if __name__ == "__main__":
#    foo = TestVcsLifecyc()
#    foo.test_lifecycle()
