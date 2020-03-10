from ..twcc.session import Session2
import os
import pytest
from click.testing import CliRunner
from ..twccli import cli


class TestSessionLifecyc:
    def _loadParams(self):
        self.runner = CliRunner()
        self.apikey = os.environ['TWCC_API_KEY']
        self.pcode = os.environ['TWCC_PROJ_CODE']
        pass

    def _init(self):
        cmd_list = "config init --apikey {} -pcode {}".format(
                self.apikey, self.pcode )
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def _whoami(self):
        cmd_list = "config whoami"
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(u" "))

    def __run(self, cmd_list):
        result = self.runner.invoke(cli, cmd_list)

        print(result.output)
        print(result)
        assert result.exit_code == 0

    def test_config_init(self):
        self._loadParams()
        self._init()

    def test_config_whoami(self):
        self._loadParams()
        self._whoami()

