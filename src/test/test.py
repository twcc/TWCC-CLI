from __future__ import print_function
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.services.base import acls, users, keypairs
from twcc.util import pp

a = users('usr1')
pp(list=a.list())
