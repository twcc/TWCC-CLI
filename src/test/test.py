#from __future__ import print_function
from twcc.services.base import acls, users, keypairs, projects, api_key
from twcc.services.jobs import jobs
from twcc.services.storage import images, volumes, snapshots, buckets
#from twcc.util import pp


#for func in [acls, users, keypairs]:
#for usr in ['usr1', 'sys']:


#a = func('sysa', debug=True)
#a._csite_ = 'k8s-taichung-default'
#for func in [images]:
#    a = func('sysa', debug=True)
#    a._csite_ = 'k8s-taichung-default'
#    pp(list=a.list())
a = keypairs('usr1', debug=False)
pp(list=a.list())
#pp(list=a.queryById("edbe47e8-093d-48a3-bcf8-3d63163a4b84"))
