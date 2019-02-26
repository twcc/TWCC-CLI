# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import yaml
from twcc.util import pp, isNone
from twcc.clidriver import ServiceOperation

# change to new-style-class https://goo.gl/AYgxqp
class GenericService(object):

    def __init__(self, debug=False):
        # current working information
        self._csite_ = "__UNDEF__"
        self._func_ = self.__class__.__name__
        self._res_type_ = "json"
        self._debug_ = debug

        self.twcc = ServiceOperation()
        self._api_key_ = self.twcc._session_.default_key
        # @todo
        try:
            self._project_id = self.twcc._session_.def_proj
            self._username = self.twcc._session_.def_username
        except:
            self._username = ""
            self._project_id = None
            print("WARNING: no default_project")

        self.twcc._debug = debug


        # map to url
        self.url_dic = None
        # map to data entries
        self.data_dic = None
        # map to get's parameter, aka ?project=898
        self.ext_get = None

        self.res_type = 'json'
        self.res_type_valid = self.twcc.res_type_valid

        self.http_verb = 'get'
        self.http_verb_valid = self.twcc.http_verb_valid

    def _chkSite_(self):
        if isNone(self._csite_):
            raise ValueError("No site value.")
        elif not self._csite_ in self.getSites():
            raise ValueError("Site value is not valid. {0}".format(self._csite_))
        else:
            return True

    def getSites(self):
        exclu = ['admin', 'harbor', 'goc', 'test_sit', 'nchc-ad', 'haproxy_stats']
        return [ x for x in self.twcc._session_.clusters if not x in exclu]

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

        res = self.twcc.doAPI(
            site_sn = self._csite_,
            key_tag = self._api_key_,
            func = self._func_,
            url_dict = self.url_dic if not isNone(self.url_dic) else None,
            data_dict = self.data_dic if not isNone(self.data_dic) else None,
            http = self.http_verb,
            url_ext_get = self.ext_get,
            res_type = self.res_type)

        if self._debug_:
            pp(res=res)

        return res

    def create(self,mid):
        pass

    def list(self):
        self.http_verb = 'get'
        self.res_type = 'json'
        return self._do_api()

    def queryById(self, mid):
        self.url_dic = { self.__class__.__name__ : mid }
        self.http_verb = 'get'
        res = self._do_api()
        self.url_dic = None
        return res

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self, proj_id):
        self._project_id = proj_id
        print (">>>", self._project_id)

    def delete(self, mid):
        self.http_verb = "delete"
        self.url_dic = { self.__class__.__name__ : mid }
        res = self._do_api()
        return res

class CpuService(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = "openstack-taichung-community"

class GpuService(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = "k8s-taichung-default"
