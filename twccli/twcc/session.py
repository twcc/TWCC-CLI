# -*- coding: utf-8 -*-
import copy
import os
import re
import yaml
import shutil
from collections import defaultdict
from twcc.util import *


# class TwccApiValidator(Validator):
#    def validate(self, document):
#        ok = re.match(
#            '^([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})$', document.text)
#        if not ok:
#            raise ValidationError(
#                message='Please enter a TWCC API key',
#                cursor_position=len(document.text))  # Move cursor to end


# custom_style_2 = style_from_dict({
#    Token.Separator: '#6C6C6C',
#    Token.QuestionMark: '#FF9D00 bold',
#    # Token.Selected: '',  # default
#    Token.Selected: '#5F819D',
#    Token.Pointer: '#FF9D00 bold',
#    Token.Instruction: '',  # default
#    Token.Answer: '#5F819D bold',
#    Token.Question: '',
# })
#
# quest_api = [
#    {
#        'type': 'input',
#        'name': 'TWCC_API_KEY',
#        'message': "Your API Key from www.TWCC.ai",
#        'validate': TwccApiValidator
#    },
# ]


class Session2(object):
    # static varibles
    PackageYaml = "{}/yaml/NCHC_API-Test_env.yaml".format(
        os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))))

    def __init__(self, twcc_data_path=None,
                 twcc_api_key=None,
                 twcc_file_session=None,
                 twcc_project_code=None):
        self.twcc_data_path = twcc_data_path
        self.twcc_api_key = Session2._getApiKey()

        if isNone(self.twcc_data_path):
            if 'TWCC_DATA_PATH' in os.environ:
                self.twcc_data_path = os.environ['TWCC_DATA_PATH']
            else:
                self.twcc_data_path = os.path.dirname(
                    os.path.realpath(__file__))

        if isNone(twcc_project_code):
            self.twcc_project_code = twcc_project_code
        else:
            self.twcc_project_code = Session2._getDefaultProject()

        self.twcc_file_session = twcc_file_session
        if isNone(self.twcc_file_session):
            self.twcc_file_session = os.path.join(
                self.twcc_data_path, "credential")
            self.twcc_file_resources = os.path.join(
                self.twcc_data_path, "resources")
        self.package_yaml = Session2.PackageYaml

        try:
            self.loadSession()
        except ValueError as err:
            print(err)
            self.initSession()

    def initSession(self):
        session_path = os.path.abspath(os.path.dirname(self.twcc_file_session))
        mkdir_p(session_path)
        with open(self.twcc_file_session, 'w') as fn:
            documents = yaml.safe_dump(
                self.getSessionData(), fn, encoding='utf-8', allow_unicode=True)
        shutil.copyfile(self.package_yaml, self.twcc_file_resources)

    def isApiKey(self):
        self.twcc_api_key = self.sessConf["_default"]["twcc_api_key"]

    def loadSession(self):
        if not isNone(self.twcc_file_session) and isFile(self.twcc_file_session):
            self.sessConf = yaml.load(
                open(self.twcc_file_session, "r").read(), Loader=yaml.SafeLoader)
            if isNone(self.sessConf):
                raise ValueError("{} is not a valid credentials file".format(
                    self.twcc_file_session))

            self.twcc_api_key = self.sessConf["_default"]["twcc_api_key"]

            self.twcc_s3_access_key = self.sessConf["_default"]["twcc_s3_access_key"]
            self.twcc_s3_secret_key = self.sessConf["_default"]["twcc_s3_secret_key"]

            # map to proj_code
            self.twcc_proj_code = self.sessConf["_default"]["twcc_proj_id"]
            self.switchProj()
            return True
        else:
            raise ValueError("Can not file session information in {}".format(
                self.twcc_file_session))

    def switchProj(self, projCode=None):
        if isNone(projCode):
            projCode = self.twcc_proj_code

        self.twcc_proj_id = self.sessConf['projects'][projCode]

    @staticmethod
    def getTwccResourses():
        config = Session2._getTwccliConfig()
        return config['production']['resources']

    @staticmethod
    def _getTwccliConfig(yaml_file=None):
        if isNone(yaml_file):
            yaml_file = Session2.PackageYaml

        return yaml.load(open(Session2.PackageYaml, 'r').read(), Loader=yaml.SafeLoader)

    @staticmethod
    def _getIsrvProjs(api_key=None):
        from twcc.services.base import projects
        # get proj info from iservice,
        # that maybe include not allow to twcc services.
        twcc_proj = projects(api_key=api_key)
        return twcc_proj.getProjects()

    def getIsrvProjs(self):
        return Session2._getIsrvProjs(api_key=self.twcc_api_key)

    @staticmethod
    def _getDefaultProject():
        if "TWCC_PROJ_ID" in os.environ:
            return os.environ["TWCC_PROJ_ID"]

    def getDefaultProject(self):
        return Session2._getDefaultProject()

    @staticmethod
    def getClusterName(abbr=None):
        config = Session2._getTwccliConfig()
        avbl_clusters = config["production"]['resources']
        if abbr in avbl_clusters:
            return avbl_clusters[abbr]
        return None

    @staticmethod
    def _getTwccS3Keys(proj_code, api_key):
        from twcc.services.base import projects
        twcc_proj = projects(api_key=api_key)
        twcc_proj.setCluster(Session2.getClusterName("COS"))
        return twcc_proj.getS3Keys(proj_code)

    def getTwccS3Keys(self):
        return Session2._getTwccS3Keys(self.getDefaultProject(), self.twcc_api_key)

    @staticmethod
    def _getTwccProjs(cluster_name, api_key=None):
        from twcc.services.base import projects
        # get twcc existing proj info,
        # that maybe include project has been expired.

        twcc_proj = projects(api_key=api_key)
        twcc_proj.setCluster(cluster_name)
        return twcc_proj.list()

    def getTwccProjs(self, cluster_name):
        return Session2._getTwccProjs(cluster_name, self.twcc_api_key)

    @staticmethod
    def _getAvblProjs(api_key=None):
        from twcc.services.base import projects

        config = Session2._getTwccliConfig()

        twcc_proj = projects(api_key=api_key)

        iserv_proj = Session2._getIsrvProjs()

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
        from twcc.services.base import Users
        twcc_api = Users(api_key=Session2._getApiKey())
        info = twcc_api.getInfo()
        if len(info) > 0:
            return info[0]
        else:
            raise KeyError("Account for API not found.")

    def whoami(self):
        return Session2._whoami(self.twcc_api_key)

    @staticmethod
    def _getApiKey():
        if 'TWCC_API_KEY' in os.environ:
            return os.environ['TWCC_API_KEY']
        else:
            print("prompt user enter API Key")

    def getApiKey(self):
        return Session2._getApiKey()

    def getSessionData(self):
        sessionData = defaultdict(dict)

        whoami = self.whoami()
        sessionData["_default"]['twcc_username'] = whoami['username']
        sessionData["_default"]['twcc_api_key'] = self.twcc_api_key
        sessionData["_default"]['twcc_proj_id'] = self.getDefaultProject()

        s3keys = self.getTwccS3Keys()
        sessionData["_default"]['twcc_s3_access_key'] = s3keys['public']['access_key']
        sessionData["_default"]['twcc_s3_secret_key'] = s3keys['public']['secret_key']

        resources = Session2.getTwccResourses()
        projects = self.getAvblProjs()
        for proj in projects:
            proj_codes = dict()
            for res in resources:
                res_name = resources[res]
                proj_codes[res] = projects[proj][res_name]
            sessionData['projects'][proj] = proj_codes

        return dict(sessionData)

    def __str__(self):
        key_values = [
            {"key": "twcc_data_path", "value": self.twcc_data_path},
            {"key": "twcc_api_key", "value": self.twcc_api_key},
            {"key": "package_yaml", "value": self.package_yaml},
            {"key": "twcc_file_session", "value": self.twcc_file_session},
            {"key": "twcc_file_resources", "value": self.twcc_file_resources},
            {"key": "twcc_proj_code", "value": self.twcc_proj_code},
        ]

        return table_layout("paramters", key_values, isPrint=False)


# if __name__ == '__main__':
    #sess = Session2()
    # print(sess)
    # print(sess.whoami())
    # print(sess.getTwccApiHost())
    # print(sess.getIsrvProjs())
    # print(sess.getTwccProjs("k8s-taichung-default"))
    # print(sess.getTwccS3Keys())
    # print(Session2._getDefaultProject())

    # print(sess.getSessionData())
    # print(sess.switchProj("ACD108162"))

def session_start():
    return Session2()
