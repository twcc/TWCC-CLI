# -*- coding: utf-8 -*-
import copy
import errno
import os
import re
from twcc.util import *
from PyInquirer import Validator, ValidationError, prompt
from PyInquirer import style_from_dict, Token

_TWCC_CLI_VERSION_="v190917"

class TwccApiValidator(Validator):
    def validate(self, document):
        ok = re.match('^([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a TWCC API key',
                cursor_position=len(document.text))  # Move cursor to end
custom_style_2 = style_from_dict({
    Token.Separator: '#6C6C6C',
    Token.QuestionMark: '#FF9D00 bold',
    #Token.Selected: '',  # default
    Token.Selected: '#5F819D',
    Token.Pointer: '#FF9D00 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#5F819D bold',
    Token.Question: '',
})

quest_api = [
    {
        'type': 'input',
        'name': 'TWCC_API_KEY',
        'message': "Your API Key from www.TWCC.ai",
        'validate': TwccApiValidator
    },
    #{
    #    'type': 'input',
    #    'name': 'TWCC_KEY_NAME',
    #    'message': "Enter Key Name for this key",
    #},
]

class Session(object):

    def __init__(self,
                 twcc_yaml_path=None,
                 twcc_session=None):

        self.files = {}
        self.twcc_yaml_path = twcc_yaml_path

        self.files["credential"] = os.path.join(
            os.environ['TWCC_DATA_PATH'], "credential")
        self.files["resources"] = os.path.join(
            os.environ['TWCC_DATA_PATH'], "resources")

        if self.is_files_exist():
            self.load_session()
        else:
            self.create_session()


    def is_files_exist(self):
        for fn in self.files.keys():
            if not os.path.isfile(self.files[fn]):
                return False
        return True

    def create_session(self):
        API_KEY = os.environ.get('TWCC_API_KEY', '')
        if not API_KEY:
            answers = prompt(quest_api)
            API_KEY = answers['TWCC_API_KEY']
        KEY_NAME = 'twcc'
        self.convertYaml(API_KEY, KEY_NAME)
        self._getProjects()
        self.load_session()

    def _getProjects(self):
        from twcc.services.base import acls, projects, users, api_key
        import json

        u = users(debug=False)
        info_usr = u.list()
        if len(info_usr)==0:
            raise

        info_usr = info_usr[0]
        sess_yaml = "twcc_username={}\n".format(info_usr['username'])
        print(u"hi, {} TWCC API-Key accepted!".format(info_usr['display_name']))

        a = projects(debug=False)
        prjs = a.getProjects()

        #k = api_key()
        #print(k.list())

        a._csite_ = 'k8s-taichung-default' # TWCC allow k8s only
        cluster = a.getSites()[0]
        avl_proj = a.list()[:9]
        #table_layout ("Proj for {0}".format(cluster), avl_proj, ['id', 'name'])
        # @todo here!
        # Check if projects are matched.
        not_in_proj = [x.get('id') for x in avl_proj if x.get('name') not in prjs.keys()]
        # Remove any project not able to show.
        avl_proj[:] = [x for x in avl_proj if x.get('id') not in not_in_proj]
        quest_api = [
            { 'type': 'rawlist',
              'name': 'default_project',
              'message': "Default *PROJECT_ID* when using TWCC-Cli:",
              'choices': [ u"{} - [ {} {} ], AVBL. CR.:{}".format(
                  x['id'], x['name'], 
                  strShorten(prjs[ x['name'] ]['prj_name']), 
                  prjs[ x['name'] ]['prj_avbl_cr'] ) for x in avl_proj ],
            }]
        PROJECT_ID = os.environ.get('TWCC_PROJECT_ID', '')
        PROJECT_CODE = os.environ.get('TWCC_PROJECT_CODE', '')
        valid_proj_ids = [p['id'] for p in avl_proj]
        if not PROJECT_ID or not PROJECT_CODE or int(PROJECT_ID) not in valid_proj_ids:
            answers = prompt(quest_api, style=custom_style_2)
            PROJECT_ID = answers['default_project'].split(" - ")[0]
            PROJECT_CODE = answers['default_project'].split(" ")[3]

        fn_cred = self.files['credential']
        sess_yaml += "twcc_proj_id={}\n".format(PROJECT_ID)

        s3_proj = projects()
        s3_proj._csite_ = 'ceph-taichung-default'
        s3_key = s3_proj.getS3Keys(PROJECT_CODE)

        sess_yaml += "twcc_s3_access_key={}\n".format(s3_key['public']['access_key'])
        sess_yaml += "twcc_s3_secret_key={}\n".format(s3_key['public']['secret_key'])

        open(fn_cred, 'a+').write(sess_yaml)


    def load_session(self):
        import re
        self.yaml = self.files['resources']

        self.credentials = {}
        cnt = open(self.files['credential'], 'r').readlines()
        for li in cnt:
            li = li.strip()
            if not re.search("^\[default]", li) and re.search("=", li):
                key, val = li.split("=")

                if key == "twcc_cli":
                    assert val==_TWCC_CLI_VERSION_, "TWCC_CLI version error! plz, `rm ~/.twcc_data` and input api-key again."

                if key == "twcc_host":
                    self.host = val
                elif key == "twcc_api_key":
                    (key_u, key_v) = val.split(":")
                    self.credentials[key_u] = key_v
                elif key == "twcc_ssh_key":
                    self.ssh_key = val
                elif key == "twcc_proj_id":
                    self.def_proj = val
                elif key == "twcc_s3_access_key":
                    self.def_s3_access_key = val
                elif key == "twcc_s3_secret_key":
                    self.def_s3_secret_key = val
                elif key == "twcc_username":
                    self.def_username = val

        if len(self.credentials.keys())>=1:
            self.default_key = list(self.credentials.keys())[0]
            #self.default_key = self.credentials.keys()

        self.clusters = {}
        import yaml
        config = yaml.load(open(self.yaml, 'r').read(), Loader=yaml.FullLoader)
        self.clusters = config[ os.environ['_STAGE_'] ]['clusters']
        del config

    def convertYaml(self, api_key, key_name):
        """
        Todo:
           * need to change
        """
        if not os.path.exists(os.environ['TWCC_DATA_PATH']):
            mkdir_p(os.environ['TWCC_DATA_PATH'])

        if not os.path.exists(self.files['resources']):
            from shutil import copyfile
            copyfile(self.twcc_yaml_path, self.files['resources'])

        if not os.path.exists(self.files['credential']):
            import yaml
            config = yaml.load(open(self.twcc_yaml_path, 'r').read(), Loader=yaml.FullLoader)
            t_config = config[os.environ['_STAGE_']]

            mbuf = ""
            if 'host' in t_config:
                mbuf += "[default]\n"
                mbuf += "twcc_host={0}\n".format(t_config['host'])
            mbuf += "twcc_api_key={0}:{1}\n".format(key_name, api_key)
            open(self.files['credential'], 'w').write(mbuf)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def session_start():
    if not '_TWCC_SESSION_' == globals():
        TWCC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return Session( twcc_yaml_path="{}/yaml/NCHC_API-Test_env.yaml".format(TWCC_PATH) )
    else:
        global _TWCC_SESSION_
        return _TWCC_SESSION_

