# -*- coding: utf-8 -*-
import copy
import os
import re
import yaml
import click
import shutil
import datetime
import requests
from collections import defaultdict
from twccli.twcc.util import isNone, isFile, mkdir_p, table_layout, send_ga
from twccli.version import __version__


class Session2(object):
    # static varibles
    PackageYaml = "{}/yaml/TWCC_API.yaml".format(
        os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))))

    isInitialized = False

    def __init__(self, twcc_data_path=None,
                 twcc_api_key=None,
                 twcc_file_session=None,
                 twcc_project_code=None,
                 user_agent=None,
                 twcc_cid=None):
        """
        Session2 controls all TWCC API required information,
        incl. api_key, s3 keys, project code, parameters in user environment.

        Keyword Arguments:
            twcc_data_path {[type]} -- [description] (default: {None})
            twcc_api_key {[type]} -- [description] (default: {None})
            twcc_file_session {[type]} -- [description] (default: {None})
            twcc_project_code {[type]} -- [description] (default: {None})

        Raises:
            ValueError: [description]
            KeyError: [description]

        Returns:
            [type] -- [description]
        """
        self.twcc_api_key = twcc_api_key
        self.twcc_cid = twcc_cid
        self.twcc_data_path = Session2._getTwccDataPath(twcc_data_path)
        self.twcc_file_session = Session2._getSessionFile(twcc_file_session)
        self.twcc_file_resources = Session2._getResourceFile()
        self.twcc_proj_code = Session2._getDefaultProject(twcc_project_code)
        self.package_yaml = Session2.PackageYaml
        self.user_agent = user_agent
        if self.isValidSession():
            self.isInitialized = True
            self.loadSession()
        else:
            self._initSession()
    @staticmethod
    def _getUserAgent():
        if 'User_Agent' in os.environ and len(os.environ['User_Agent']) > 0:
            return os.environ['User_Agent']
        else:
            yaml = Session2._isValidSession(isConfig=True)
            if type(yaml) == bool:
                return None
            else:
                if 'user_agent' in yaml['_meta']:
                    return yaml['_meta']['user_agent']
                else:
                    return None

    def _initSession(self):

        session_path = os.path.abspath(os.path.dirname(self.twcc_file_session))
        mkdir_p(session_path)
        with open(self.twcc_file_session, 'w') as fn:
            try:
                documents = yaml.safe_dump(
                    Session2._getSessionData(self.twcc_api_key, self.twcc_proj_code, self.twcc_cid), fn, encoding='utf-8', allow_unicode=True)
            except requests.exceptions.ConnectionError:
                raise ValueError(click.style("Please check Project Code and APIKEY", bg='red', fg='white', blink=True, bold=True))

            from os import sys, path
            sys.path.append(path.dirname(path.abspath(__file__)))
            from services.generic import GenericService
            cli = GenericService()
            fun_call = '_'.join([i for i in sys.argv[1:] if re.findall(r'\d',i) == [] and not i == '-sv']).replace('-','')
            cli._send_ga(fun_call)

        #if not twcc_cid == None:
        #    ua = user_agent if not user_agent == None else ''
        #    ga_params = {'geoid':sessionData["_meta"]['ga_country'], 'ua':ua,"version":sessionData['_meta']['cli_version'],"func":'config_init',"p_version":sys.version.split(' ')[0]}
        #    send_ga('config_init',sessionData['_meta']['ga_cid'],ga_params)

        shutil.copyfile(self.package_yaml, self.twcc_file_resources)

    def isApiKey(self):
        self.twcc_api_key = self.sessConf["_default"]["twcc_api_key"]

    @staticmethod
    def _getTwccDataPath(twcc_data_path=None):
        if isNone(twcc_data_path):
            if 'TWCC_DATA_PATH' in os.environ:
                return os.environ['TWCC_DATA_PATH']
            else:
                return os.path.dirname(os.path.realpath(__file__))
        return twcc_data_path

    @staticmethod
    def _getSessionFile(twcc_file_session=None):
        if isNone(twcc_file_session):
            return os.path.join(Session2._getTwccDataPath(), "credential")
        return twcc_file_session

    @staticmethod
    def _getResourceFile(twcc_file_resources=None):
        if isNone(twcc_file_resources):
            return os.path.join(Session2._getTwccDataPath(), "resources")
        else:
            return twcc_file_resources

    @staticmethod
    def _isValidSession(isConfig=False):
        twcc_file_session = Session2._getSessionFile()
        if not isNone(twcc_file_session) and isFile(twcc_file_session):
            sessConf = yaml.load(
                open(twcc_file_session, "r").read(), Loader=yaml.SafeLoader)
            if not type(sessConf) == type(None):
                if isConfig:
                    return sessConf
                else:
                    return True
        return False

    def isValidSession(self):
        return Session2._isValidSession()

    def loadSession(self):
        if self.isValidSession():
            self.sessConf = yaml.load(
                open(self.twcc_file_session, "r").read(), Loader=yaml.SafeLoader)
            if isNone(self.sessConf):
                raise ValueError("{} is not a valid credentials file".format(
                    self.twcc_file_session))

            self.twcc_username = self.sessConf["_default"]["twcc_username"]
            self.twcc_api_key = self.sessConf["_default"]["twcc_api_key"]
            self.twcc_s3_access_key = self.sessConf["_default"]["twcc_s3_access_key"]
            self.twcc_s3_secret_key = self.sessConf["_default"]["twcc_s3_secret_key"]

            # map to proj_code
            self.twcc_proj_code = self.sessConf["_default"]["twcc_proj_code"]
            self.switchProj()
            return True

    def switchProj(self, projCode=None):
        if isNone(projCode):
            projCode = self.twcc_proj_code

        self.twcc_proj_id = self.sessConf['projects'][projCode]

    @staticmethod
    def _getTwccResourses():
        config = Session2._getTwccliConfig()
        return config['production']['resources']

    @staticmethod
    def _getTwccliConfig(yaml_file=None):
        if isNone(yaml_file):
            yaml_file = Session2.PackageYaml

        return yaml.load(open(Session2.PackageYaml, 'r').read(), Loader=yaml.SafeLoader)

    @staticmethod
    def _getIsrvProjs(api_key=None):
        from twccli.twcc.services.base import projects
        twcc_proj = projects(api_key=api_key)
        return twcc_proj.getProjects(isAll=True, is_table=False, is_print=False)

    def getIsrvProjs(self):
        return Session2._getIsrvProjs(api_key=self.twcc_api_key)

    @staticmethod
    def _getDefaultProject(twcc_proj_code=None):
        if isNone(twcc_proj_code):
            if "_TWCC_PROJECT_CODE_" in os.environ and not isNone(os.environ['_TWCC_PROJECT_CODE_']):
                return os.environ["_TWCC_PROJECT_CODE_"]
            if Session2._isValidSession():
                return Session2._isValidSession(isConfig=True)['_default']['twcc_proj_code']
            raise ValueError("input project code")
        return twcc_proj_code

    def getDefaultProject(self):
        return Session2._getDefaultProject()

    @staticmethod
    def _getClusterName(abbr=None):
        config = Session2._getTwccliConfig()
        avbl_clusters = config["production"]['resources']
        if abbr in avbl_clusters:
            return avbl_clusters[abbr]
        return None

    def getClusterName(self, abbr=None):
        return Session2._getClusterName(abbr)

    @staticmethod
    def _getTwccS3Keys(proj_code, api_key):
        from twccli.twcc.services.base import projects
        twcc_proj = projects(api_key=api_key)
        twcc_proj.setCluster(Session2._getClusterName("COS"))
        return twcc_proj.getS3Keys(proj_code)

    def getTwccS3Keys(self):
        return Session2._getTwccS3Keys(Session2.getDefaultProject(), self.twcc_api_key)

    @staticmethod
    def _getTwccProjs(cluster_name, api_key=None):
        from twccli.twcc.services.base import projects
        # get twcc existing proj info,
        # that maybe include project has been expired.

        twcc_proj = projects(api_key=api_key)
        twcc_proj.setCluster(cluster_name)
        return twcc_proj.list()

    def getTwccProjs(self, cluster_name):
        return Session2._getTwccProjs(cluster_name, self.twcc_api_key)

    @staticmethod
    def _getAvblProjs(api_key=None):
        from twccli.twcc.services.base import projects

        config = Session2._getTwccliConfig()

        twcc_proj = projects(api_key=api_key)

        iserv_proj = Session2._getIsrvProjs(api_key=api_key)

        twcc_proj = defaultdict(dict)

        avbl_clusters = config["production"]['resources']
        for cluster in avbl_clusters:
            cluster_name = avbl_clusters[cluster]
            projs = Session2._getTwccProjs(cluster_name, api_key=api_key)
            for ele in projs:
                twcc_proj[ele['name']][avbl_clusters[cluster]] = ele['id']

        # intersect two project set so user can use in twcc-cli
        avbl_prjs = set(twcc_proj.keys()).intersection(set(iserv_proj.keys()))

        avbl_prjs_info = dict()
        for prj_code in avbl_prjs:
            if float(iserv_proj[prj_code]['prj_avbl_cr']) > 0:
                avbl_prjs_info[prj_code] = iserv_proj[prj_code]
                avbl_prjs_info[prj_code].update(twcc_proj[prj_code])
        return avbl_prjs_info

    def getAvblProjs(self):
        return Session2._getAvblProjs(api_key=self.twcc_api_key)

    @staticmethod
    def _getTwccApiHost():
        config = Session2._getTwccliConfig()
        return config['production']['host']

    def getTwccApiHost(self):
        return Session2._getTwccApiHost()

    @staticmethod
    def _whoami(api_key=None):
        from twccli.twcc.services.base import Users
        twcc_api = Users(api_key=api_key)
        info = twcc_api.getInfo()
        if info == {'message': 'Your request is unauthorized. Key is expired.'}:
            print(info)
            exit(1)
        if len(info) > 0:
            return info[0]
        else:
            raise KeyError("Account for API not found.")

    def whoami(self):
        return Session2._whoami(self.twcc_api_key)

    @staticmethod
    def _getApiKey(twcc_api_key):
        if '_TWCC_API_KEY_' in os.environ and len(os.environ['_TWCC_API_KEY_']) > 0:
            return os.environ['_TWCC_API_KEY_']
        else:
            if Session2._isValidSession():
                return Session2._isValidSession(isConfig=True)['_default']['twcc_api_key']
            else:
                # raw_input("_getApiKey(twcc_api_key) " + twcc_api_key)
                if not isNone(twcc_api_key):
                    return twcc_api_key
                else:
                    raise ValueError("Not existing API Key.")

    def getApiKey(self):
        return Session2._getApiKey()

    @staticmethod
    def _getSessionData(twcc_api_key=None, proj_code=None, twcc_cid=None):
        import sys
        import json
        import requests as rq
        url = 'http://ipinfo.io/json'
        res = rq.get(url)
        sessionData = defaultdict(dict)
        whoami = Session2._whoami(twcc_api_key)
        sessionData["_default"]['twcc_username'] = whoami['username']
        sessionData["_default"]['twcc_api_key'] = twcc_api_key
        sessionData["_default"]['twcc_proj_code'] = Session2._getDefaultProject(
            proj_code)
        if not twcc_cid == None:
            sessionData["_meta"]['ga_cid'] = twcc_cid
        sessionData["_meta"]['ga_country']  = json.loads(res.text)['country']
        sessionData["_meta"]['ctime'] = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')
        sessionData["_meta"]['cli_version'] = __version__
        user_agent = Session2._getUserAgent()
        if not isNone(user_agent):
            sessionData["_meta"]['user_agent'] = user_agent
        
        s3keys = Session2._getTwccS3Keys(
            Session2._getDefaultProject(proj_code), Session2._getApiKey(twcc_api_key))
        sessionData["_default"]['twcc_s3_access_key'] = s3keys['public']['access_key']
        sessionData["_default"]['twcc_s3_secret_key'] = s3keys['public']['secret_key']
        resources = Session2._getTwccResourses()
        projects = Session2._getAvblProjs(twcc_api_key)
        for proj in projects:
            proj_codes = dict()
            for res in resources:
                res_name = resources[res]
                proj_codes[res] = projects[proj][res_name]
            sessionData['projects'][proj] = proj_codes


        return dict(sessionData)

    def __str__(self):
        from datetime import datetime

        key_values = [
            {"key": "_TWCC_API_KEY_", "value": self.twcc_api_key},
            {"key": "_TWCC_PROJECT_CODE_", "value": self.twcc_proj_code},
            {"key": "session_created_time", "value":
                self.sessConf['_meta']['ctime']},
            {"key": "twcc_cli_version",
                "value": self.sessConf['_meta']['cli_version']},
            {"key": "twcc_apikey_owner", "value": Session2._whoami(self.twcc_api_key)[
                'display_name']},
            {"key": "twcc_data_path", "value": self.twcc_data_path},
            {"key": "package_yaml", "value": self.package_yaml},
            {"key": "twcc_file_session", "value": self.twcc_file_session},
            {"key": "twcc_file_resources", "value": self.twcc_file_resources},
        ]
        # return ""
        return table_layout("parameters", key_values, ['key', 'value'], isPrint=False, isWrap=False)


# if __name__ == '__main__':
#     sess = Session2()
    # print(sess.whoami())
    # print(sess.twcc_proj_code)
    # print(sess.getTwccApiHost())
    # print(sess.getIsrvProjs())
    # print(sess.getTwccProjs("k8s-taichung-default"))
    # print(sess.getTwccS3Keys())
    # print(Session2._getDefaultProject())

    # print(sess.getSessionData())
    # print(sess.switchProj("ACD108162"))

def session_start():
    return Session2()
