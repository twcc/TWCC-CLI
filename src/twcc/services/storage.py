# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import CpuService, GenericService

class volumes(CpuService):
    def __init__(self, api_key_tag, debug=False):
        CpuService.__init__(self, debug=debug)

        self._api_key_ = api_key_tag

class snapshots(CpuService):
    def __init__(self, api_key_tag, debug=False):
        CpuService.__init__(self, debug=debug)

        self._api_key_ = api_key_tag

class images(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = 'harbor'
        self._api_key_ = api_key_tag
        self.res_type = "txt"

class buckets(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = 'ceph-taichung-default'
        self._api_key_ = api_key_tag
