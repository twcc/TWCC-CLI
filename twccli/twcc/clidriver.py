# -*- coding: utf-8 -*-
import time
import re
import requests
import json
import yaml
import datetime
import logging
from twccli.twccli import pass_environment, logger
import os
from .session import Session2
from .util import parsePtn, isNone, isDebug, pp, twcc_error_echo
import urllib3
urllib3.disable_warnings()


class ServiceOperation:
    def __init__(self, api_key=None):
        self.api_key = Session2._getApiKey(api_key)
        self._load()
        self.http_verb_valid = set(['get', 'post', 'delete', 'patch', 'put'])
        self.res_type_valid = set(['txt', 'json'])

        # for site usage
        self.header_extra = {}

        self._debug = isDebug()
        # if self._debug:
        #     self._setDebug()

    def _load(self):
        # raw_input("in clidriver "+self.api_key)
        self.twcc_config = Session2._getTwccliConfig()
        self.host_url = Session2._getTwccApiHost()

        _ava_funcs_ = self.twcc_config['avalible_funcs']
        self.valid_funcs = [
            _ava_funcs_[x]['name'] for x in range(len(_ava_funcs_))
        ]

        self.valid_http_verb = dict([(_ava_funcs_[x]['name'],
                                      _ava_funcs_[x]['http_verb'])
                                     for x in range(len(_ava_funcs_))])
        self.url_format = dict([(_ava_funcs_[x]['name'],
                                 _ava_funcs_[x]['url_type'])
                                for x in range(len(_ava_funcs_))])
        self.url_ptn = dict([(x, parsePtn(self.url_format[x]))
                             for x in self.url_format.keys()])

    def load_credential(self):
        # @todo
        self.api_keys = self._session_.credentials
        self.host_url = self._session_.host
        # @todo aug 0206
        try:
            self.def_s3_access_key = self._session_.twcc_s3_access_key
            self.def_s3_secret_key = self._session_.twcc_s3_secret_key
        except Exception as e:
            print(e)
            self.def_proj = ""

    def load_yaml(self):
        self._yaml_fn_ = Session2.PackageYaml
        twcc_conf = Session2._getTwccliConfig()
        self.stage = os.environ['_STAGE_']

        # change to load ~/.twcc_data/credential
        #self.host_url = twcc_conf[self.stage]['host']
        #self.api_keys = twcc_conf[self.stage]['keys']

        _ava_funcs_ = twcc_conf['avalible_funcs']

        self.valid_funcs = [
            _ava_funcs_[x]['name'] for x in range(len(_ava_funcs_))
        ]
        self.valid_http_verb = dict([(_ava_funcs_[x]['name'],
                                      _ava_funcs_[x]['http_verb'])
                                     for x in range(len(_ava_funcs_))])
        self.url_format = dict([(_ava_funcs_[x]['name'],
                                 _ava_funcs_[x]['url_type'])
                                for x in range(len(_ava_funcs_))])
        self.url_ptn = dict([(x, parsePtn(self.url_format[x]))
                             for x in self.url_format.keys()])

        self.twcc_conf = twcc_conf

    def isFunValid(self, func):
        return True if func in self.valid_funcs else False

    def _to_curl(self, t_api, t_headers, t_data=None, mtype="get"):

        headers = ['"{0}: {1}"'.format(k, v) for k, v in t_headers.items()]
        headers = " \\\n -H ".join(headers)

        if isNone(t_data):
            command = "curl -s -X {method} \\\n -H {headers} \\\n '{uri}'"
            return command.format(method=mtype.upper(),
                                  headers=headers,
                                  data=t_data,
                                  uri=t_api)
        else:
            command = "curl -s -X {method} \\\n -H {headers} \\\n -d '{data}' \\\n '{uri}'"
            return command.format(method=mtype.upper(),
                                  headers=headers,
                                  data=t_data,
                                  uri=t_api)

    def _api_act(self,
                 t_api,
                 t_headers,
                 t_data=None,
                 mtype="get",
                 show_curl=False):

        if show_curl:
            self._to_curl(t_api, t_headers, t_data, mtype)

        start_time = time.time()
        ssl_verify_mode = True

        if mtype == 'get':
            r = requests.get(t_api, headers=t_headers, verify=ssl_verify_mode)

        elif mtype == 'post':
            r = requests.post(t_api,
                              headers=t_headers,
                              data=json.dumps(t_data),
                              verify=ssl_verify_mode)
        elif mtype == "delete":
            r = requests.delete(t_api, headers=t_headers,
                                verify=ssl_verify_mode)
        elif mtype == "patch":
            r = requests.patch(t_api,
                               headers=t_headers,
                               data=json.dumps(t_data),
                               verify=ssl_verify_mode)
        elif mtype == "put":
            r = requests.put(t_api,
                             headers=t_headers,
                             data=json.dumps(t_data),
                             verify=ssl_verify_mode)
        else:
            raise ValueError("http verb:'{0}' is not valid".format(mtype))

        if self._debug:
            logger.info(t_api)
            logger.info(t_headers)
            logger.info("--- URL: %s, Status: %s, (%.3f sec) ---" %
                        (t_api, r.status_code, time.time() - start_time))
        return (r, (time.time() - start_time))

    def doAPI(self,
              site_sn=None,
              api_host=None,
              key_tag=None,
              api_key=None,
              user_agent=None,
              ctype="application/json",
              func=None,
              url_dict=None,
              data_dict=None,
              url_ext_get=None,
              http='get',
              res_type='json'):


        if not self.isFunValid(func):
            raise ValueError("Function for:'{0}' is not valid".format(func))
        if not http in set(self.valid_http_verb[func]):
            raise ValueError("http verb:'{0}' is not valid".format(http))

        mkAPIUrl_v3 = False
        if http == 'get' or http == 'put' or http == 'patch':
            mkAPIUrl_v3 = True
        t_url = self.mkAPIUrl(site_sn, api_host, func,
                              url_dict=url_dict, is_v3=mkAPIUrl_v3)
        t_header = self.mkHeader(site_sn=site_sn,
                                 key_tag=key_tag,
                                 api_host=api_host,
                                 api_key=api_key,
                                 user_agent=user_agent,
                                 ctype=ctype)
        if not isNone(url_ext_get):
            t_url += "?"
            t_url_tmp = []
            for param_key in url_ext_get.keys():
                t_url_tmp.append("{0}={1}".format(param_key,
                                                  url_ext_get[param_key]))
            t_url += "&".join(t_url_tmp)
        res = self._api_act(t_url, t_header, t_data=data_dict, mtype=http)

        import sys
        if 'click' in sys.modules.keys() and res[0].status_code >= 400:
            twcc_error_echo(res[0].json()['detail'])
            sys.exit(1)

        return self._std_output_(res, t_url, res_type)


    def _std_output_(self, res, t_url, res_type):
        if res_type in self.res_type_valid:
            if res_type == 'json':
                try:
                    return res[0].json(), t_url
                except:
                    return res[0].content, t_url
            elif res_type == 'txt':
                return res[0].content, t_url
        else: 
            raise ValueError(
                "Response type Error:'{0}' is not valid, available options: {1}"
                .format(res_type, ", ".join(self.res_type_valid)))
        return res

    def mkHeader(self,
                 site_sn=None,
                 key_tag=None,
                 api_host=None,
                 api_key=None,
                 user_agent=None,
                 ctype="application/json"):

        self.api_host = api_host

        self.ctype = ctype

        from twccli.version import __version__
        if not user_agent == None:
            this_user_agent = user_agent
        else:
            this_user_agent = 'TWCC-CLI v%s' % (__version__)
        return_header = {
            'User-Agent': this_user_agent,
            'X-API-HOST': site_sn,
            'x-api-key': api_key,
            'Content-Type': self.ctype
        }

        if len(self.header_extra.keys()) > 0:
            for key in self.header_extra.keys():
                return_header[key] = self.header_extra[key]

        return return_header

    def _setDebug(self):
        log_dir = "{}/log".format(os.environ['TWCC_DATA_PATH'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = datetime.datetime.now().strftime(
            log_dir + "/nchc_%Y%m%d_%H%M%S.log")
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S',
            filename=log_filename)
        # 定義 handler 輸出 sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # 設定輸出格式
        formatter = logging.Formatter(
            '%(name)-12s: %(levelname)-8s %(message)s')
        # handler 設定輸出格式
        console.setFormatter(formatter)
        # 加入 hander 到 root logger
        logging.getLogger('').addHandler(console)

        # wrapper
        self._i = logging.info
        self._d = logging.debug
        self._w = logging.warning

    def show(self):
        logger.info("-" * 10 + "=" * 10 +
                    " [info] BEGIN " + "=" * 10 + "-" * 10)
        logger.info("-" * 10 + "=" * 10 +
                    " [info] ENDS  " + "=" * 10 + "-" * 10)

    def mkAPIUrl(self, site_sn=None, api_host=None, func=None, url_dict=None, is_v3=True):

        # check if this function valid
        if not self.isFunValid(func):
            raise ValueError("API Function:'{0}' is not valid".format(func))

        url_ptn = self.url_ptn[func]
        url_str = self.url_format[func]
        url_parts = {}
        # check if this site_sn is valid
        if not type(site_sn) == type(None):
            self.api_pf = site_sn
        else:
            self.api_pf = api_host

        if "PLATFORM" in url_ptn.keys():
            url_parts['PLATFORM'] = self.api_pf

        # given url_dict
        ptn = func
        if not type(url_dict) == type(None):
            # check if function name is in given url_dict
            if func in url_dict:
                ptn = "%s/%s" % (func, url_dict[func])
                del url_dict[func]

                ptn += "/" + "/".join(
                    ["%s/%s" % (k, url_dict[k]) for k in url_dict.keys()])

                # todos
                ptn = ptn.strip("/")
            else:
                raise ValueError(
                    "Can not find '{0}' in provided dictionary.".format(func))

        if "FUNCTION" in url_ptn.keys():
            url_parts["FUNCTION"] = ptn

        t_url = url_str
        for ptn in url_parts.keys():
            t_url = t_url.replace(url_ptn[ptn], url_parts[ptn])

        # need to migrate /v3/
        if 'PLATFORM' in url_parts and url_parts[
                'PLATFORM'] in ["openstack-taichung-default-2", "k8s-taichung-default"] and 'sites' in url_parts['FUNCTION']:
            if is_v3:
                t_url = t_url.replace("/v2/", "/v3/")
        return self.host_url + t_url


def isV3(fun_str):
    if fun_str == "sites":
        return True
    if "sites" in fun_str and "action" in fun_str:
        return True
    if len(set(fun_str.split("/")).intersection(set(['images', 'save']))) == 2:
        return True
    return False
