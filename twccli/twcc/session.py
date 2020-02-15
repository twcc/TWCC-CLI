# -*- coding: utf-8 -*-
import copy
import os
import re
import yaml
import shutil
from collections import defaultdict
# from twcc import _TWCC_SESSION_
from .util import *
# print(_TWCC_SESSION_)

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

    isInitialized = False

    def __init__(self, twcc_data_path=None,
                 twcc_api_key=None,
                 twcc_file_session=None,
                 twcc_project_code=None):
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

        self.twcc_api_key = Session2._getApiKey()
        self.twcc_data_path = Session2._getTwccDataPath(twcc_data_path)
        self.twcc_file_session = Session2._getSessionFile(twcc_file_session)
        self.twcc_file_resources = Session2._getResourceFile()
        self.twcc_proj_code = Session2._getDefaultProject(twcc_project_code)
        self.package_yaml = Session2.PackageYaml

        if self.isValidSession():
            self.isInitialized = True
            self.loadSession()
            print("load session")
            print(">>>", self.twcc_proj_id)
            print(">>>", self.twcc_s3_access_key)
        else:
            # print(self.getSessionData())
            self.isInitialized = False
            self.initSession()
            print("init session")

    def initSession(self):
        session_path = os.path.abspath(os.path.dirname(self.twcc_file_session))
        mkdir_p(session_path)
        with open(self.twcc_file_session, 'w') as fn:
            documents = yaml.safe_dump(
                self.getSessionData(), fn, encoding='utf-8', allow_unicode=True)
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(">>>>>>>>>>>>>>>>>>> write to file <<<<<<<<<<<<<<<<<<<<<<<<<<<")
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
    def _isValidSession():
        twcc_file_session = Session2._getSessionFile()
        print("twcc_file_session:", twcc_file_session)
        print("rule 1:", not isNone(twcc_file_session))
        print("rule 2:", not isFile(twcc_file_session))
        if not isNone(twcc_file_session) and isFile(twcc_file_session):
            sessConf = yaml.load(
                open(twcc_file_session, "r").read(), Loader=yaml.SafeLoader)
            # print(sessConf)
            if not type(sessConf) == type(None):
                return True
        return False

    def isValidSession(self):
        return Session2._isValidSession()

    def loadSession(self):
        # if isNone(_TWCC_SESSION_) and type(_TWCC_SESSION_) == type(Session2) and _TWCC_SESSION_.isInitialized:
        #     return _TWCC_SESSION_
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
        from twcc.services.base import projects
        # get proj info from iservice,
        # that maybe include not allow to twcc services.
        twcc_proj = projects(api_key=api_key)
        return twcc_proj.getProjects()

    def getIsrvProjs(self):
        return Session2._getIsrvProjs(api_key=self.twcc_api_key)

    @staticmethod
    def _getDefaultProject(twcc_proj_code=None):
        if isNone(twcc_proj_code):
            if "TWCC_PROJ_CODE" in os.environ:
                print(os.environ["TWCC_PROJ_CODE"])
                return os.environ["TWCC_PROJ_CODE"]
            else:
                print("input project code")
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
        from twcc.services.base import projects
        print(">>>", proj_code)
        twcc_proj = projects(api_key=api_key)
        twcc_proj.setCluster(Session2._getClusterName("COS"))
        return twcc_proj.getS3Keys(proj_code)

    def getTwccS3Keys(self):
        return Session2._getTwccS3Keys(Session2.getDefaultProject(), self.twcc_api_key)

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

    @staticmethod
    def _getSessionData():
        sessionData = defaultdict(dict)

        whoami = Session2._whoami()
        sessionData["_default"]['twcc_username'] = whoami['username']
        sessionData["_default"]['twcc_api_key'] = Session2._getApiKey()
        sessionData["_default"]['twcc_proj_code'] = Session2._getDefaultProject()

        s3keys = Session2._getTwccS3Keys(
            Session2._getDefaultProject(), Session2._getApiKey())
        sessionData["_default"]['twcc_s3_access_key'] = s3keys['public']['access_key']
        sessionData["_default"]['twcc_s3_secret_key'] = s3keys['public']['secret_key']

        resources = Session2._getTwccResourses()
        projects = Session2._getAvblProjs()
        for proj in projects:
            proj_codes = dict()
            for res in resources:
                res_name = resources[res]
                proj_codes[res] = projects[proj][res_name]
            sessionData['projects'][proj] = proj_codes

        return dict(sessionData)

    def getSessionData(self):
        return Session2._getSessionData()

    def __str__(self):
        print("---"*10, self.twcc_proj_code)
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
