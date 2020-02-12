# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import defaultdict
from twcc.util import isNone
from twcc.services.generic import GenericService


class Users(GenericService):
    def __init__(self, api_key=None):
        GenericService.__init__(self, skip_session=True)

        self._csite_ = "goc"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getInfo(self):
        return self.list()

    def getAccountInfo(self):
        info = self.list()
        if len(info) > 0:
            info = info[0]
            detail = self.queryById(info['id'])
            prj_id_role = defaultdict(list)
            for ele in detail['associating_projects']:
                prj_id_role[ele['name']].append(ele)

            for prj_name in prj_id_role:
                print(prj_name)
            # print(prj_id_role)
        else:
            raise KeyError("Account for API not found.")


class users(GenericService):
    def __init__(self, api_key=None, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "goc"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getInfo(self):
        return self.list()


class image_commit(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "goc"

    def getCommitList(self):
        return self._do_api()

    def createCommit(self, siteid, tag, image):
        self.http_verb = "post"
        self.data_dic = {"site": siteid, "tag": tag, "image": image}
        self.res_type = "txt"
        return self._do_api()


class acls(GenericService):
    """ This Class is for ACL api call
    """

    def __init__(self, debug=False):
        """ constractor for this ACL class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self, debug=debug)

        self._csite_ = "admin"
        self.res_type = "json"

    def getSites(self):
        res = self.list()
        return sorted([x['group'] for x in res['data']])

    def listGroup(self):
        """ this api is the same with acl

        """
        self._func_ = "acls-g"
        return self._do_api()


class keypairs(GenericService):
    """ This Class is for keypairs api call
    """

    def __init__(self, api_key_tag, debug=False):
        """ constractor for this keypairs class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self)
        # current working information
        self._csite_ = "openstack-taichung-suse"
        self._api_key_ = api_key_tag
        self._debug_ = debug

    def list(self):
        return self._do_api()

    def createKeyPair(self, keyPairName):
        self.http_verb = "post"
        self.data_dic = {"name": keyPairName}
        self.res_type = "txt"
        res = self._do_api()
        return res


class projects(GenericService):
    """
    """

    def __init__(self, api_key=None):
        GenericService.__init__(self, api_key=None, skip_session=True)

        if not isNone(api_key):
            self.api_key = api_key
        self._csite_ = "goc"

    def setCluster(self, cluster_name=None):
        if not isNone(cluster_name):
            self._csite_ = cluster_name

    def getProjectSolution(self, proj_id, sol_id):
        self.url_dic = {'projects': proj_id, 'solutions': sol_id}
        return self.list()

    def getProjects(self):
        s = iservice(api_key=self._api_key_)
        res = s.getAllProjects()

        my_prj = {}
        for prj in res['wallet']:

            prj_code = prj[u"計畫系統代碼"]
            prj_avbl_cr = float(prj[u"錢包餘額"])
            prj_name = prj[u"計畫名稱"]
            prj_ele = {'prj_code': prj_code,
                       'prj_avbl_cr': prj_avbl_cr,
                       'prj_name': prj_name}
            my_prj[prj_code] = prj_ele
        return my_prj

    def getS3ProjId(self, proj_code):
        projs = self.list()
        for proj in projs:
            if proj['name'] == proj_code:
                return proj['id']

    def getS3Keys(self, proj_code):
        proj_id = self.getS3ProjId(proj_code)
        self.url_dic = {'projects': proj_id, 'key': ''}
        return self.list()

class api_key(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)
        self._csite_ = "admin"

    def getInfo(self):
        self.url_dic = {'api_key': 'api_key'}
        self._csite_ = 'admin'
        return self.list()


class iservice(GenericService):
    def __init__(self, api_key=api_key):
        GenericService.__init__(self, api_key=api_key, skip_session=True)

    def getAllProjects(self):
        self.url_dic = {"iservice": "user/all_wallet"}
        return self.list()
