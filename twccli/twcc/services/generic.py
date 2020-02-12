# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import yaml
import twcc
from twcc.session import Session2
from twcc.util import pp, isNone, isDebug
from twcc.clidriver import ServiceOperation

# change to new-style-class https://goo.gl/AYgxqp

class GenericService(object):

    def __init__(self, api_key=None, initSession=False):
        # current working information
        self._csite_ = "__UNDEF__"
        self._func_ = self.__class__.__name__
        self._res_type_ = "json"
        self._debug_ = isDebug()

        self.twcc = ServiceOperation()
        if type(api_key) == type(None):
            # here, while Session2 using this class,
            # we don't really need session to assist
            self._api_key_ = Session2._getApiKey()
        else:
            print("using passed api_key", api_key)
            self._api_key_ = api_key

        self.twcc_session = twcc._TWCC_SESSION_
        self._project_code = self.twcc_session.getDefaultProject()
        self.project_ids = self.twcc_session.twcc_proj_id
        self.twcc._debug = isDebug()

        self.cluster_tag = "CNTR"
        
        # set defult project id
        self._project_id = self.twcc_session.twcc_proj_id[self.cluster_tag]
        self._csite_ = Session2._getClusterName( self.cluster_tag )
        
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
            raise ValueError(
                "Site value is not valid. {0}".format(self._csite_))
        else:
            return True

    def getSites(self):
        exclu = ['admin', 'harbor', 'goc',
                 'test_sit', 'nchc-ad', 'haproxy_stats']
        return [x for x in self.twcc._session_.clusters if not x in exclu]

    def _isAlive(self):
        return self.twcc.try_alive()

    def _do_api(self):
        if self._debug_:
            pp(csite=self._csite_,
                func=self._func_,
                res_type=self.res_type)

            if not isNone(self.url_dic):
                pp(url_dic=self.url_dic)
            if not isNone(self.data_dic):
                pp(data_dic=self.data_dic)

        res = self.twcc.doAPI(
            site_sn=self._csite_,
            api_key=self._api_key_,
            func=self._func_.lower(),
            url_dict=self.url_dic if not isNone(self.url_dic) else None,
            data_dict=self.data_dic if not isNone(self.data_dic) else None,
            http=self.http_verb,
            url_ext_get=self.ext_get,
            res_type=self.res_type)

        if self._debug_:
            pp(res=res)

        return res

    def create(self, mid):
        pass

    def list(self):
        self.http_verb = 'get'
        self.res_type = 'json'
        return self._do_api()

    def queryById(self, mid):
        self.url_dic = {self._func_: mid}
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

    def delete(self, mid):
        self.http_verb = "delete"
        self.url_dic = {self.__class__.__name__: mid}
        res = self._do_api()
        return res

    def __log(self, mstr):
        if self._debug_:
            print("DEBUG in [{}]: {}".format(self.__class__.__name__, mstr))


class CpuService(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self._csite_ = "openstack-taichung-community"


class GpuService(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.cluster_tag = "CNTR"
        self._csite_ = "k8s-taichung-default"


if __name__ == "__main__":
    ga = GenericService()
    print(ga)
