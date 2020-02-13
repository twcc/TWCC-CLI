from click.testing import CliRunner
import os
import sys
from os.path import abspath, dirname
import click
import unittest

# set project src dir
sys.path.insert(0, os.path.join(abspath(dirname('__file__')), 'twccli'))

from examples.twccli import cli

def test_list_cntr():
    runner = CliRunner()
    result = runner.invoke(cli, ['ls', '-c'])
    assert result.exit_code == 0


def test_list_cos():
    runner = CliRunner()
    result = runner.invoke(cli, ['ls', '-o'])
    assert result.exit_code == 0

