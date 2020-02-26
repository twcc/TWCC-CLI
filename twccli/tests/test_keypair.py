# -*- coding: utf-8 -*-
from click.testing import CliRunner
from twcc import _TWCC_SESSION_, Session2
import click
from examples.twccli import cli
import pytest
import uuid


class TestKeypairLifecyc:
    def _loadParams(self):
        self.key_name = "test_{}".format(str(uuid.uuid1()).split("-")[0])

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
        cmd_list = u"mk v -key --name {}".format(self.key_name)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def _list(self):
        cmd_list = "ls v -key {}".format(self.key_name)
        self.list_out = self.__run(cmd_list.split(" "))
        print(self.list_out)

    def _delete(self):
        cmd_list = "rm v -key --force {}".format(self.key_name)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))


    def test_lifecycle(self):
        self._loadParams()
        self._loadSession()
        self._create()
        self._list()
        self._delete()

if __name__ == "__main__":
    foo = TestKeypairLifecyc()
    foo.test_lifecycle()
