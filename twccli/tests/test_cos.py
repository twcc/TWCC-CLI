# -*- coding: utf-8 -*-
from click.testing import CliRunner
import os
import re
import click
import json
from ..twccli import cli
import pytest
import uuid
import subprocess
import random


class TestCosLifecyc:

    def _loadSession(self):
        self.runner = CliRunner()

    def _loadParams(self):
        rand = random.randint(0, 1000)
        self.bk_name = "bucket{}".format(str(rand))
        self.dir = "dir_{}".format(str(rand))

    def __run(self, cmd_list):
        print(cmd_list)
        result = self.runner.invoke(cli, cmd_list)
        print(result.output)
        #assert result.exit_code == 0
        return result.output

    def _create_bucket(self, bk):
        cmd_list = "mk cos -bkt {}".format(bk)
        print(cmd_list)
        self.create_out = self.__run(cmd_list.split(" "))

    def _del_bucket(self, bkt):
        cmd_list = "rm cos -bkt {} -r -f".format(bkt)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _list_bucket_after_delete(self):
        cmd_list = "ls cos -json"
        print(cmd_list)
        self.list_out = self.__run(cmd_list.split(" "))
        out = json.loads(self.list_out)

        flag = True
        for ele in out:
            if ele['Name'] == self.bk_name:
                flag = False

        assert flag

    def _upload_files(self, bk, dir):
        cmd_list = "cp cos -upload -src {} -dest {} -r".format(dir, bk)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _op_folder(self, bk, dir, op):
        cmd_list = "cp cos -bkt {} -dir {} -sync {}".format(bk, dir, op)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _download_files(self, bk, dir):
        cmd_list = "cp cos -download -src {} -dest {} -r".format(bk, dir)
        print(cmd_list)
        out = self.__run(cmd_list.split(" "))

    def _mk_download_dir(self, downDir):
        cmd = ["mkdir", downDir]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()

    def _remove_file(self, fn):
        cmd = ["rm", fn]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()

    def _remove_dir(self, updir, downdir):
        cmd1 = ["rm", "-rf", updir]
        cmd2 = ["rm", "-rf", downdir]
        print(cmd1)
        p = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        p.communicate()
        print(cmd2)
        p = subprocess.Popen(cmd2, stdout=subprocess.PIPE)
        p.communicate()

    def _create_download_dir(self, dir):
        cmd = ["mkdir", dir]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()

    def _create_upload_file(self, file):
        cmd = ["touch", file]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()

    def _remove_upload_file(self, file):
        cmd = ["rm", file]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()


    def _chk_bkt_versioning(self):
        cmd_list = "ch cos --bucket-name {} --enable-versioning".format(
            self.bk_name)
        print(cmd_list)
        self.__run(cmd_list.split(" "))

        cmd_list = "ls cos --check-versioning --json-view".format(self.bk_name)
        print(cmd_list)
        out = json.loads(self.__run(cmd_list.split(" ")))
        bkt_info = [x for x in out if x['Name'] == self.bk_name]
        assert bkt_info[0]['Versioning'] == 'Enabled'

        cmd_list = "ch cos --bucket-name {} --disable-versioning".format(
            self.bk_name)
        print(cmd_list)
        self.__run(cmd_list.split(" "))

        cmd_list = "ls cos --check-versioning --json-view".format(self.bk_name)
        print(cmd_list)
        out = json.loads(self.__run(cmd_list.split(" ")))
        bkt_info = [x for x in out if x['Name'] == self.bk_name]
        assert bkt_info[0]['Versioning'] == 'Suspended'

    # HERE is the test

    def test_create_bucket(self):
        self._loadSession()
        self._loadParams()
        self._create_bucket(self.bk_name)
        self._chk_bkt_versioning()
        self._del_bucket(self.bk_name)
        self._list_bucket_after_delete()
