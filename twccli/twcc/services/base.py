# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from twccli.twcc.session import Session2
from collections import defaultdict
from twccli.twcc.util import isNone, jpp, table_layout
from twccli.twcc.services.generic import GenericService


class Users(GenericService):
    def __init__(self, api_key=None):
        # raw_input("in users "+api_key)
        GenericService.__init__(self, skip_session=True, api_key=api_key)
        self._func_ = 'users'
        self._csite_ = "goc"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getInfo(self):
        return self.list()

    def getHFS(self, is_table):
        info = self.list()
        if len(info) > 0:
            info = info[0]
            detail = self.queryById(info['id'])
            gpfs = detail['gpfs']
            total_gpfs = []
            for key in gpfs.keys():
                gpfs[key]['dictionary'] = key
                total_gpfs.append((gpfs[key]))
            cols = ['dictionary', 'usage', 'default_quota',
                    'extra_quota', 'expired_date', 'last_updated_time']
            if is_table:
                table_layout("HFS Result",
                             total_gpfs,
                             cols,
                             isPrint=True,
                             isWrap=False)
            else:
                jpp(total_gpfs)
        else:
            raise KeyError("Account for API not found.")

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
    def __init__(self, api_key=None):
        GenericService.__init__(self)

        self._csite_ = "goc"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getInfo(self):
        return self.list()


class image_commit(GenericService):
    def __init__(self, debug=False):
        GenericService.__init__(self)

        self._csite_ = "goc"

    def getCommitList(self):
        return table_layout("commited images", self._do_api(), isPrint=False, isWrap=False)

    def createCommit(self, siteid, tag, image):
        self.http_verb = "post"
        self.data_dic = {"site": siteid, "tag": tag, "image": image}
        self.res_type = "txt"
        self._do_api()


class ApiKey(GenericService):
    def __init__(self, api_key=None):

        GenericService.__init__(self, api_key=api_key, skip_session=True)
        self._csite_ = "admin"
        self._func_ = "api_key"
        if not isNone(api_key):
            self._api_key_ = api_key

    def list(self):
        print("in list"*3, self._api_key_)
        self.http_verb = 'get'
        self.res_type = 'json'
        return self._do_api()


class acls(GenericService):
    """ This Class is for ACL api call
    """

    def __init__(self, api_key=None):

        GenericService.__init__(self, api_key=api_key, skip_session=True)
        self._csite_ = "admin"
        self._func_ = "acls"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getSites(self):
        res = self.list()
        return sorted([x['group'] for x in res['data']])

    def listGroup(self):
        """ this api is the same with acl

        """
        self._func_ = "acls-g"
        return self._do_api()


class Keypairs(GenericService):
    """ This Class is for keypairs api call
    """

    def __init__(self):
        """ constractor for this keypairs class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self)
        self._func_ = "keypairs"
        self._csite_ = Session2._getClusterName("VCS")

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
        self.api_key = api_key
        GenericService.__init__(self, api_key=api_key, skip_session=True)

        self._csite_ = "goc"

    def setCluster(self, cluster_name=None):
        if not isNone(cluster_name):
            self._csite_ = cluster_name

    def getProjectSolution(self, proj_id, sol_id):
        self.url_dic = {'projects': proj_id, 'solutions': sol_id}
        return self.list()

    def getProjects(self, isAll=False, is_table=True, is_print=True):
        s = iservice(api_key=self._api_key_)
        my_prj = {}
        total_prj = []
        cols = ['prj_name', 'prj_code', 'prj_avbl_cr']
        if isAll == True:
            res = s.getProjects(isAll)
            if 'wallet' in res:
                for prj in res['wallet']:
                    prj_code = prj[u"計畫系統代碼"]
                    prj_avbl_cr = float(prj[u"錢包餘額"])
                    prj_name = prj[u"計畫名稱"]
                    prj_ele = {
                        # 'su_qouta':prj['su_qouta'],
                        # 'obtained_su':prj['obtained_su'],
                        'prj_code': prj_code,
                        'prj_avbl_cr': prj_avbl_cr,
                        'prj_name': prj_name}
                    total_prj.append(prj_ele)
                    my_prj[prj_code] = prj_ele
            if not is_print:
                return my_prj
            my_prj = total_prj
            res = res['wallet']
        else:
            res_all = s.getProjects(isAll=True)
            res = s.getProjects()
            wallet_code = res['wallet_code']
            my_prj = {}
            my_prj_otherinfo = {}
            for prj in res_all['wallet']:
                if prj[u'錢包ID'] == wallet_code:
                    my_prj = {
                        'prj_name': prj[u"計畫名稱"],
                        'prj_code': prj[u"計畫系統代碼"],
                        'time': prj[u"計畫開始時間"]+'-'+prj[u"計畫結束時間"],
                        'wallet_owner': prj[u"錢包擁有者"],
                        'person_quota': int(float(res['su_qouta'])),
                        'person_Tquota': int(float(res['obtained_su'])),
                        'project_quota': int(float(res['prj_su_quota'])),
                        'project_Tquota': int(float(res['prj_obtained_su']))

                    }

            # my_prj['one'] = res
            # my_prj['all'] = res_all
            res['prj_code'] = my_prj['prj_code']
            cols = ['prj_name', 'prj_code', 'time', 'person_quota',
                    'person_Tquota', 'project_quota', 'project_Tquota', 'wallet_owner']
        if is_table:
            table_layout("Project Result",
                         my_prj,
                         cols,
                         isPrint=True,
                         isWrap=False)
        else:
            jpp(res)

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
    def __init__(self, api_key=None):
        GenericService.__init__(self, api_key=api_key, skip_session=True)

    def getProjects(self, isAll=False):
        if isAll:
            self.url_dic = {"iservice": "user/all_wallet"}
        else:
            self.url_dic = {"iservice": "user/wallet"}
        return self.list()

    def getProducts(self):
        # self.ext_get = {}
        self.url_dic = {"iservice": "projects/products/AI"}
        return self.list()

    def getVCSProducts(self):
        """先不處理這個功能，因為產品/價格還沒穩定

        """
        prod = self.getProducts()

        def filter(x):
            return True if re.search("^v\..*super", x['spec']) and not re.search("^v\.12", x['spec']) else False

        return [x for x in prod if filter(x)]


class Flavors(GenericService):
    def __init__(self, csite, api_key=None):
        GenericService.__init__(self, skip_session=True)
        self._func_ = self.__class__.__name__.lower()
        self._csite_ = csite
        if not isNone(api_key):
            self._api_key_ = api_key
