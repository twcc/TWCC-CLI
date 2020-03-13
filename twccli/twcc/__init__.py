import os, sys
from twccli.twcc.util import isNone
from twccli.twcc.session import Session2
from requests.packages import urllib3

if sys.version_info[0] == 2:
    # fix utf8 for py27
    # sys.setdefaultencoding() does not exist, here!
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding('UTF8')

#
# Get our data path to be added to botocore's search path
#
if "HOME" in os.environ:
    _TWCC_data_path_ = os.path.join(os.environ['HOME'], '.twcc_data')
else:
    _TWCC_data_path_ = "/tmp"

os.environ['TWCC_DATA_PATH'] = _TWCC_data_path_

GupSiteBlockSet = set([182, 29, 35, 120])


# By default, requests logs following message if verify=False
#   InsecureRequestWarning: Unverified HTTPS request is
#   being made. Adding certificate verification is strongly advised.
# Just disable the warning if user intentionally did this.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
