# -*- coding: utf-8 -*-
from click.testing import CliRunner
from twcc import Session2
import click
from twccli import cli
import pytest


env_options = {"cicd_pytorch": (1, "PyTorch", "pytorch-19.11-py3:latest"),
               "cicd_tensorflow": (1, "TensorFlow", "tensorflow-19.11-tf2-py3:latest"),
               "cicd_test0gpu": (0, u"影像檔測試區", "ngc/nvidia/tensorrt-19.08-py3:latest")}

class TestCntrLifecyc:
    def _loadParams(self):
        test_env = "cicd_test0gpu"
        env_pick = env_options[test_env]
        self.cntr_name = test_env
        (self.gpu_num, self.sol, self.img_name) = env_pick

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

    def _create(self):
        cmd_list = u"mk ccs -name {} -gpu {} -sol {} -img {} -wait".format(self.cntr_name, self.gpu_num
        , self.sol, self.img_name)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def _list(self):
        import re
        match = re.search('SiteId: (?P<site_id>[0-9]*)\.', self.create_out)
        self.site_id = match.group('site_id')
        assert type(int(self.site_id)) == type(1)
        cmd_list = "ls ccs {}".format(self.site_id)
        self.list_out = self.__run(cmd_list.split(" "))
        print(self.list_out)

    def _listDetail(self, isatt=True):
        cmd_list = "ls ccs --port {}".format(self.site_id)
        out = self.__run(cmd_list.split(" "))
        out = out.split("\n")
        print(out)
        import json
        if isatt:
            flg = False
            print(">>>"*14, type(out[-2]))
            for exp_port in json.loads(out[-2].replace("\'", "\"").replace("u\"", "\"")):
                if exp_port['target_port'] == 3000:
                    flg = True
            assert flg
        else:
            flg = True
            for exp_port in json.loads(out[-2].replace("\'", "\"").replace("u\"", "\"")):
                if exp_port['target_port'] == 3000:
                    flg = False
            assert flg


    def _exposedPort(self):
        cmd_list = "net ccs -s {} -exp -p 3000".format(self.site_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _unexposedPort(self):
        cmd_list = "net ccs -s {} -unexp -p 3000".format(self.site_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _delete(self):
        cmd_list = "rm ccs {}".format(self.site_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))


    def test_lifecycle(self):
        self._loadParams()
        self._loadSession()
        self._create()
        self._list()
        self._exposedPort()
        self._listDetail(isatt=True)
        self._unexposedPort()
        self._listDetail(isatt=False)
        self._delete()

#if __name__ == "__main__":
#    foo = TestCntrLifecyc()
#    foo.test_lifecycle()
