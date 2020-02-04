from __future__ import print_function
from os import sys, path
sys.path.append(path.dirname(path.abspath(__file__)))
from generic import GenericService


class flavors(GenericService):

    def __init__(self, api_key):
        GenericService.__init__(self)
        self._csite_ = "openstack-taichung-community"
        self._api_key_ = api_key

