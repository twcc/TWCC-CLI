from click.testing import CliRunner
import os
import sys
from os.path import abspath, dirname
import click
import unittest

# set project src dir
sys.path.insert(0, os.path.join(abspath(dirname('__file__')), 'twccli'))


def test_hello_world():
    @click.command()
    @click.argument('name')
    def hello(name):
        click.echo('Hello %s!' % name)

    runner = CliRunner()
    result = runner.invoke(hello, ['Peter'])
    assert result.exit_code == 0
    assert result.output == 'Hello Peter!\n'


if __name__ == '__main__':
    test_envVaribles()
