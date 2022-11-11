import os
import sys
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

if "TWCC_DATA_PATH" in os.environ and os.path.isdir(os.environ['TWCC_DATA_PATH']):
    pass
else:
    homepath = os.environ['HOME'] if 'HOME' in os.environ else os.environ['HOMEPATH']
    os.environ['TWCC_DATA_PATH'] = os.path.join(homepath, '.twcc_data')

GupSiteBlockSet = set([182, 29, 35, 120])


# By default, requests logs following message if verify=False
#   InsecureRequestWarning: Unverified HTTPS request is
#   being made. Adding certificate verification is strongly advised.
# Just disable the warning if user intentionally did this.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
