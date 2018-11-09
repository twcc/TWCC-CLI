from __future__ import print_function
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.services.base import acls, users, keypairs, projects
from twcc.services.jobs import jobs
from twcc.services.storage import images, volumes, snapshots, buckets
from twcc.util import pp

#for func in [acls, users, keypairs]:
#for usr in ['usr1', 'sys']:

a = projects('sys', debug=False)

pp(list=len(a.list()))

