# -*- coding: utf-8 -*-
from __future__ import print_function
from twccli.twcc.services.generic import CpuService
from twccli.twcc.services.base import projects
from twccli.twcc.util import pp, isNone, table_layout


class Networks(CpuService):
    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "networks"

    def list(self):
        self.ext_get = {'project': self._project_id}
        return self._do_api()

    def create(self, name, getway, cidr):
        self.http_verb = 'post'
        self.data_dic = {'project': self._project_id, 'name': name,
                         'gateway': getway, 'cidr': cidr, "with_router": True}
        return self._do_api()

    def isStable(self, vnet_id):
        vnet_info = self.queryById(vnet_id)
        return vnet_info['status'] == "ACTIVE"

    def delete(self, vnet_id):
        self.http_verb = 'delete'
        self.url_dic = {'networks': vnet_id}
        # self.data_dic = {'network_id ': vnet_id}
        return self._do_api()
