# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import re
import sys
import yaml
import traceback
from twccli.twcc.session import Session2
from twccli.twcc.util import isNone, isDebug, timezone2local, send_ga
from twccli.twcc.clidriver import ServiceOperation
from twccli.twccli import logger

# change to new-style-class https://goo.gl/AYgxqp


class GenericService(object):

    def __init__(self, api_key=None, cluster_tag=None, skip_session=False):
        # current working information
        self._csite_ = "__UNDEF__"
        self._func_ = self.__class__.__name__
        self._res_type_ = "json"
        self._debug_ = isDebug()
        self._api_key_ = Session2._getApiKey(api_key)
        self._user_agent = Session2._getUserAgent()
        self.twcc = ServiceOperation(api_key=api_key)

        self.twcc._debug = isDebug()

        self.cluster_tag = cluster_tag
        if isNone(self.cluster_tag):
            self.cluster_tag = "CNTR"

        if not skip_session:

            self.twcc_session = Session2()
            self._project_code = self.twcc_session.getDefaultProject()
            self.project_ids = self.twcc_session.twcc_proj_id
            self._project_id = self.twcc_session.twcc_proj_id[self.cluster_tag]

        # set defult project id
        self._csite_ = Session2._getClusterName(self.cluster_tag)

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

    def _send_ga(self, event_name, t_url=None):
        twcc_file_session = Session2._getSessionFile()
        sessConf = yaml.load(
            open(twcc_file_session, "r").read(), Loader=yaml.SafeLoader)

        if not sessConf == None and 'ga_cid' in sessConf['_meta']:
            func_call_stack = []
            for trace_line in traceback.format_stack():
                funcs = re.findall(r'in ([_A-Za-z]+)', trace_line)
                if funcs:
                    func_call_stack.extend(funcs)

            ua = '' if self._user_agent == None else self._user_agent
            country = sessConf['_meta']['ga_country'] if 'ga_country' in sessConf['_meta'] else ''
            func_list = ','.join(func_call_stack)[','.join(
                func_call_stack).rindex('invoke'):].split(',')[1:-3]
            ga_params = {'geoid': country, 'ua': ua, "version": sessConf['_meta']['cli_version'], "func": '-'.join(
                func_list), "p_version": sys.version.split(' ')[0]}

            if event_name == 'do_api':
                ga_params = {'func': ','.join(func_list), 'url': t_url, 'geoid': country, 'ua': ua,
                             "version": sessConf['_meta']['cli_version'], "func": '-'.join(func_list), "p_version": sys.version.split(' ')[0]}
            send_ga(event_name, sessConf['_meta']['ga_cid'], ga_params)

    def _do_api(self):
        if self._debug_:
            logger_info = {'csite': self._csite_,
                           'func': self._func_, 'res_type': self.res_type}
            if not isNone(self.url_dic):
                logger_info.update({'url_dic': self.url_dic})
            if not isNone(self.data_dic):
                logger_info.update({'data_dic': self.data_dic})
            logger.info(logger_info)

        res, t_url = self.twcc.doAPI(
            site_sn=self._csite_,
            api_key=self._api_key_,
            user_agent=self._user_agent,
            func=self._func_.lower(),
            url_dict=self.url_dic if not isNone(self.url_dic) else None,
            data_dict=self.data_dic if not isNone(self.data_dic) else None,
            http=self.http_verb,
            url_ext_get=self.ext_get,
            res_type=self.res_type)

        if self._debug_:
            logger.info({'res': res})
            self._send_ga('do_api', t_url=t_url)

        if type(res) == type([]):
            for eachone in res:
                if 'create_time' in eachone:
                    eachone['create_time'] = timezone2local(
                        eachone['create_time']).strftime("%Y-%m-%d %H:%M:%S")
        elif type(res) == type({}):
            if 'create_time' in res:
                res['create_time'] = timezone2local(
                    res['create_time']).strftime("%Y-%m-%d %H:%M:%S")
            if 'message' in res and 'request is unauthorized' in res['message']:
                raise ValueError("API Key is not validated.")
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
        self.url_dic = {self._func_: mid}
        res = self._do_api()
        return res

    def __log(self, mstr):
        if self._debug_:
            print("DEBUG in [{}]: {}".format(self.__class__.__name__, mstr))


class CpuService(GenericService):
    def __init__(self):
        GenericService.__init__(self, cluster_tag="VCS")

    def getQuota(self, isAll=False):
        if isAll:
            self._func_ = "projects"
            self.url_dic = {"projects": "%s/user_quotas" % (self._project_id)}
        else:
            self._func_ = "project_quotas"
            self.url_dic = {"project_quotas": ""}
            self.ext_get = {"project": self._project_id}
        return self.list()


class GpuService(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.cluster_tag = "CNTR"
        self._csite_ = Session2._getClusterName(self.cluster_tag)

    def getQuota(self, isAll=False):
        if isAll:
            self._func_ = "projects"
            self.url_dic = {"projects": "%s/user_quotas" % (self._project_id)}
        else:
            self._func_ = "project_quotas"
            self.url_dic = {"project_quotas": ""}
            self.ext_get = {"project": self._project_id}
        return self.list()
