# -*- coding: utf-8 -*-

import copy
import errno
import os
import re
from twcc.util import *


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

        if isNone(twcc_session):
            self.create_session()

        else:
            self._session = twcc_session

    def create_session(self):
        self.convertYaml()
        self.load_session()

    def load_session(self):
        self.yaml = self.files['resources']

        self.credentials = {}
        cnt = open(self.files['credential'], 'r').readlines()
        for li in cnt:
            li = li.strip()
            if not re.search("^\[default]", li):
                key, val = li.split("=")

                if key == "twcc_host":
                    self.host = val
                elif key == "twcc_api_key":
                    (key_u, key_v) = val.split(":")
                    self.credentials[key_u] = key_v

    def convertYaml(self):
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
            config = yaml.load(open(self.twcc_yaml_path, 'r').read())
            t_config = config[os.environ['_STAGE_']]

            mbuf = ""
            if 'host' in t_config:
                mbuf += "[default]\n"
                mbuf += "twcc_host={0}\n".format(t_config['host'])
            if 'keys' in t_config:
                for usr in t_config['keys']:
                    mbuf += "twcc_api_key={0}:{1}\n".format(usr,
                                                            t_config['keys'][usr])

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
    return Session(
        twcc_yaml_path="/home/fychao/Working/twcc-cli/src/yaml/NCHC_API-Test_env.yaml")
    
