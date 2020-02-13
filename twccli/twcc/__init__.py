# Copyright 2018 NCHC
import os
from twcc.session import Session2
from requests.packages import urllib3
from requests.packages.urllib3 import exceptions as urllib3_exceptions

__version__ = '0.0.1'

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

_TWCC_SESSION_ = Session2()

# By default, requests logs following message if verify=False
#   InsecureRequestWarning: Unverified HTTPS request is
#   being made. Adding certificate verification is strongly advised.
# Just disable the warning if user intentionally did this.
urllib3.disable_warnings(urllib3_exceptions.InsecureRequestWarning)