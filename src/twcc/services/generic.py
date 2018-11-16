# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import yaml
from twcc.util import pp, isNone
from twcc.clidriver import ServiceOperation

class GenericService():

    def __init__(self, debug=False):
        # current working information
        self._csite_ = "__UNDEF__"
        self._api_key_ = "__UNDEF__"
        self._func_ = self.__class__.__name__
        self._res_type_ = "json"
        self._debug_ = debug

        self.twcc = ServiceOperation()
        self.twcc._debug = debug

        # map to url
        self.url_dic = None
        # map to data entries
        self.data_dic = None

        self.res_type = 'json'
        self.res_type_valid = self.twcc.res_type_valid
        self.http_verb = 'get'
        self.http_verb_valid = self.twcc.http_verb_valid

    def _isAlive(self):
        return self.twcc.try_alive()

    def _do_api(self):
        if self._debug_:
            pp(csite=self._csite_,
                func=self._func_,
                yaml=self.twcc._yaml_fn_,
                res_type=self.res_type)

            if not isNone(self.url_dic):
                pp(url_dic=self.url_dic)
            if not isNone(self.data_dic):
                pp(data_dic=self.data_dic)

        if not isNone(self.url_dic):
            res = self.twcc.doAPI(
                site_sn=self._csite_,
                key_tag=self._api_key_,
                func=self._func_,
                url_dict=self.url_dic,
                http=self.http_verb,
                res_type=self.res_type)
        elif not isNone(self.data_dic):
            res = self.twcc.doAPI(
                site_sn=self._csite_,
                key_tag=self._api_key_,
                func=self._func_,
                data_dict=self.data_dic,
                http=self.http_verb,
                res_type=self.res_type)
        else:
            res = self.twcc.doAPI(
                site_sn=self._csite_,
                key_tag=self._api_key_,
                func=self._func_,
                http=self.http_verb,
                res_type=self.res_type)

        if self._debug_:
            pp(res=res)

        return res

    def create(self):
        pass

    def list(self):
        return self._do_api()

    def queryById(self, mid):
        self.url_dic = { self.__class__.__name__ : mid }
        res = self._do_api()
        self.url_dic = None
        return res

    def delete(self):
        pass


class CpuService(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = "openstack-taichung-community"

class GpuService(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = "k8s-taichung-default"
