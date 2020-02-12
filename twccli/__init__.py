import os
import sys
from os.path import abspath, join, dirname
from twcc.session import Session2
sys.path.insert(0, os.path.join(abspath(dirname('__file__')), 'twccli'))

__version__ = "0.5"
