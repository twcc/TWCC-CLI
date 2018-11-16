from __future__ import print_function
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.services.base import acls, users, keypairs, projects, api_key
from twcc.services.jobs import jobs
from twcc.services.storage import images, volumes, snapshots, buckets
from twcc.util import pp

#for func in [acls, users, keypairs]:
#for usr in ['usr1', 'sys']:


#for func in [images]:
#    a = func('sys', debug=False)
#    pp(list=a.list())
a = api_key('sys', debug=True)
pp(list=a.list())
pp(list=a.queryById("760df307-689e-45b9-bd59-9421d479f5f9"))
