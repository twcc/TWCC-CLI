# -*- coding: utf-8 -*-
from __future__ import print_function
from twccli.twcc.services.generic import GpuService, CpuService, GenericService
from twccli.twcc.session import Session2


class Volumes(CpuService):
    def __init__(self, debug=False):
        CpuService.__init__(self)
        self._func_ = "volumes"
        self._csite_ = Session2._getClusterName("VCS")

    def create(self, name, size, desc="", volume_type="hdd"):
        self.http_verb = 'post'
        self.data_dic = {'project': self._project_id, "name": name,
                         "size": size, "desc": desc, "volume_type": volume_type}
        return self._do_api()

    def deleteById(self, sys_vol_id):
        self.http_verb = 'delete'
        # self.res_type = 'txt'
        self.url_dic = {"images": sys_vol_id}
        return self._do_api()


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
