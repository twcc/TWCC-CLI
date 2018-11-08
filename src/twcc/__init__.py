# Copyright 2018 NCHC
import os
from session import session_start

__version__ = '0.0.1'

#
# Get our data path to be added to botocore's search path
#
_TWCC_data_path_ = []
if 'TWCC_DATA_PATH' in os.environ:
    for path in os.environ['TWCC_DATA_PATH'].split(os.pathsep):
        path = os.path.expandvars(path)
        path = os.path.expanduser(path)
        _TWCC_data_path.append(path)
_TWCC_data_path_.append(
    os.path.join(os.environ['HOME'], '.twcc_data')
)
os.environ['TWCC_DATA_PATH'] = os.pathsep.join(_TWCC_data_path_)


SCALAR_TYPES = set([
    'string', 'float', 'integer', 'long', 'boolean', 'double',
    'blob', 'timestamp'
])
COMPLEX_TYPES = set(['structure', 'map', 'list'])

__all__ = ["clidriver", "util", "services"]

os.environ['_STAGE_'] = "production"

_session_ = session_start()
