from click.testing import CliRunner
import os
import sys
from os.path import abspath, dirname
import click
import unittest

# set project src dir
sys.path.insert(0, os.path.join(abspath(dirname('__file__')), 'twccli'))


def test_create_twcc_session():
    import twcc
    twcc._TWCC_SESSION_
