# -*- coding: utf-8 -*-
from click.testing import CliRunner
import os
import click
import json
import pytest
from ..twcc.session import Session2
from ..twccli import cli


env_options = {"cicd_pytorch": (1, "PyTorch", "pytorch-19.11-py3:latest"),
               "cicd_tensorflow": (1, "TensorFlow", "tensorflow-19.11-tf2-py3:latest"), }


class TestCntrLifecyc:
    def _loadParams(self):
        test_env = "cicd_pytorch"
        env_pick = env_options[test_env]
        self.apikey = os.environ['_TWCC_API_KEY_']
        self.pcode = os.environ['_TWCC_PROJECT_CODE_']
        self.cntr_name = test_env
        (self.gpu_num, self.sol, self.img_name) = env_pick

    def _loadSession(self):
        self.runner = CliRunner()

    def __run(self, cmd_list):
        result = self.runner.invoke(cli, cmd_list)

        print(result.output)
        print(result)
        assert result.exit_code == 0
        return result.output

    def _create(self):
        cmd_list = u"mk ccs -n {} -gpu {} -itype {} -img {} -wait -json".format(
            self.cntr_name, self.gpu_num, self.sol, self.img_name)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))
        ans = json.loads(self.create_out)
        self.site_id = int(ans['id'])

    def _list(self):
        assert type(int(self.site_id)) == type(1)
        cmd_list = "ls ccs -s {}".format(self.site_id)
        self.list_out = self.__run(cmd_list.split(" "))

    def _listDetail(self, isatt=True):
        cmd_list = "ls ccs --port {} -json".format(self.site_id)
        out = self.__run(cmd_list.split(" "))
        out = json.loads(out)

        if isatt:
            flg = False
            for exp_port in out:
                if exp_port['target_port'] == 3000:
                    flg = True
            assert flg
        else:
            flg = True
            for exp_port in out:
                if exp_port['target_port'] == 3000:
                    flg = False
            assert flg

    def _exposedPort(self):
        cmd_list = "net ccs -s {} -open -p 3000".format(self.site_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _unexposedPort(self):
        cmd_list = "net ccs -s {} -close -p 3000".format(self.site_id)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _delete(self):
        cmd_list = ["rm", "ccs", "-f", "%s" % self.site_id]
        print(" ".join(cmd_list))
        out = self.__run(cmd_list)

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


if __name__ == "__main__":
    TestCntrLifecyc().test_lifecycle()
