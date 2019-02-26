# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import GenericService
from twcc.services.base import projects
from twcc.util import pp, isNone, table_layout


class networks(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = 'openstack-taichung-community'
        self._api_key_ = api_key_tag

    def list(self):
        self.ext_get = {'project': self._project_id}
        return self._do_api()

    def create(self):
        self.http_verb = 'post'
        return self._do_api()
