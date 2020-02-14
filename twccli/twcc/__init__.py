# Copyright 2018 NCHC
import os, sys
from twcc.util import isNone
from twcc.session import Session2
from requests.packages import urllib3

#
# Get our data path to be added to botocore's search path
#
_TWCC_data_path_ = []
if 'TWCC_DATA_PATH' in os.environ:
    for path in os.environ['TWCC_DATA_PATH'].split(os.pathsep):
        path = os.path.expandvars(path)
        path = os.path.expanduser(path)
        _TWCC_data_path_.append(path)


if "HOME" in os.environ:
    _TWCC_data_path_.append(
        os.path.join(os.environ['HOME'], '.twcc_data')
    )
else:
    _TWCC_data_path_.append("/tmp")

os.environ['TWCC_DATA_PATH'] = os.pathsep.join(_TWCC_data_path_)

SCALAR_TYPES = set([
    'string', 'float', 'integer', 'long', 'boolean', 'double',
    'blob', 'timestamp'
])
COMPLEX_TYPES = set(['structure', 'map', 'list'])

__all__ = ["clidriver", "util", "services"]

GupSiteBlockSet = set([182, 29, 35, 120])

#modulename = 'twcc.session'
#if modulename in sys.modules:
#    print(hasattr(twcc, "_TWCC_SESSION_"))
_TWCC_SESSION_ = None
while True:
    _TWCC_SESSION_ = Session2()
    # print("_TWCC_SESSION_.isInitialized", _TWCC_SESSION_.isInitialized)
    if _TWCC_SESSION_.isInitialized:
        break
    else:
        print("XXXX create again")


# By default, requests logs following message if verify=False
#   InsecureRequestWarning: Unverified HTTPS request is
#   being made. Adding certificate verification is strongly advised.
# Just disable the warning if user intentionally did this.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
