from click.testing import CliRunner
import os
import sys
from os.path import abspath, dirname
import click
import unittest
from twcc import Session2
from examples.twccli import cli

def test_init_twcc_session():
    import shutil
    import os
    shutil.rmtree( os.path.dirname(Session2._getSessionFile()) )
    assert Session2._getApiKey() == os.environ.get('TWCC_API_KEY')

def test_load_twcc_session():
    mySession = Session2()
    assert mySession.getApiKey() == Session2._getApiKey()


def test_list_cntr():
    runner = CliRunner()
    result = runner.invoke(cli, ['ls', '-c'])
    assert result.exit_code == 0


def test_list_cos():
    runner = CliRunner()
    result = runner.invoke(cli, ['ls', '-o'])
    assert result.exit_code == 0

