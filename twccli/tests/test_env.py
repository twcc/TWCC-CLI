from click.testing import CliRunner
import os
import sys
from os.path import abspath, dirname
import click
import unittest
from twcc import Session2

def test_init_twcc_session():

    import shutil
    import os
    shutil.rmtree( os.path.dirname(Session2._getSessionFile()) )
    assert Session2._getApiKey() == os.environ.get('TWCC_API_KEY') 

def test_load_twcc_session():
    mySession = Session2()
    assert mySession.getApiKey() == Session2._getApiKey()

