# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import CpuService
from twcc.services.base import projects
from twcc.util import pp, isNone, table_layout

class Networks(CpuService):
    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "networks"

    def list(self):
        self.ext_get = {'project': self._project_id}
        return self._do_api()

    def create(self):
        self.http_verb = 'post'
        return self._do_api()
