# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.session import Session2
from collections import defaultdict
from twcc.util import isNone, table_layout
from twcc.services.generic import GenericService


class Users(GenericService):
    """This class is for Users information checking
    #TODO

    :param GenericService: [description]
    :type GenericService: [type]
    :raises KeyError: [description]
    :return: [description]
    :rtype: [type]
    """    
    def __init__(self, api_key=None):
        """constractor for this Users class
        #TODO

        :param api_key: [description], defaults to None
        :type api_key: [type], optional
        """        
        GenericService.__init__(self, skip_session=True)

        self._csite_ = "goc"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getInfo(self):
        """get information
        #TODO
        
        :return: [description]
        :rtype: [type]
        """        
        return self.list()

    def getAccountInfo(self):
        """get account information
        #TODO
        
        :raises KeyError: "Account for API not found"
        """        
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
    """This class is for users ?what
    #TODO
    
    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """    
    def __init__(self, api_key=None, debug=False):
        """constractor for this users class
        
        :param api_key: [description], defaults to None
        :type api_key: [type], optional
        :param debug: [description], defaults to False
        :type debug: bool, optional
        """        
        GenericService.__init__(self, debug=debug)

        self._csite_ = "goc"
        if not isNone(api_key):
            self._api_key_ = api_key

    def getInfo(self):
        """get info
        #TODO
        
        :return: returm info list
        :rtype: [type]
        """        
        return self.list()


class image_commit(GenericService):
    """This class is for image commit
    #TODO

    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """    
    def __init__(self, debug=False):
        """constractor for this image_commit class
        
        :param debug: [description], defaults to False
        :type debug: bool, optional
        """        
        GenericService.__init__(self)

        self._csite_ = "goc"

    def getCommitList(self):
        """get commit list
        
        :return: return commited image
        :rtype: [type]
        """        
        return table_layout("commited images", self._do_api(), isPrint=False, isWrap=False)

    def createCommit(self, siteid, tag, image):
        """create commit
        
        :param siteid: [description]
        :type siteid: tuple
        :param tag: [description]
        :type tag: tuple
        :param image: [description]
        :type image: tuple
        :return: [description]
        :rtype: [type]
        """        
        self.http_verb = "post"
        self.data_dic = {"site": siteid, "tag": tag, "image": image}
        self.res_type = "txt"
        return table_layout("commited images", self._do_api(), isPrint=False)


class acls(GenericService):
    """This Class is for ACL api call
    
    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """

    def __init__(self, debug=False):
        """constractor for this ACL class
        #TODO
        :param debug: [description], defaults to False
        :type debug: bool, optional
        """        
        """ constractor for this ACL class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self, debug=debug)

        self._csite_ = "admin"
        self.res_type = "json"

    def getSites(self):
        """get sites
        
        :return: [description]
        :rtype: [type]
        """        
        res = self.list()
        return sorted([x['group'] for x in res['data']])

    def listGroup(self):
        """this api is the same with acl
        
        :return: [description]
        :rtype: [type]
        """
        self._func_ = "acls-g"
        return self._do_api()


class Keypairs(GenericService):
    """This Class is for keypairs api call
    
    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """

    def __init__(self):
        """ constractor for this keypairs class
        #TODO
        """        
        """ constractor for this keypairs class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self)
        self._func_ = "keypairs"
        self._csite_ = Session2._getClusterName("VCS")

    def list(self):
        """list
        
        :return: [description]
        :rtype: [type]
        """        
        return self._do_api()

    def createKeyPair(self, keyPairName):
        """create key pair
        
        :param keyPairName: key pair name
        :type keyPairName: tuple
        :return: [description]
        :rtype: bytes
        """        
        self.http_verb = "post"
        self.data_dic = {"name": keyPairName}
        self.res_type = "txt"
        res = self._do_api()
        return res


class projects(GenericService):
    """projects
    
    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """    
    def __init__(self, api_key=None):
        """constractor for this projects class
        
        :param api_key: [description], defaults to None
        :type api_key: [type], optional
        """        
        GenericService.__init__(self, api_key=None, skip_session=True)

        if not isNone(api_key):
            self.api_key = api_key
        self._csite_ = "goc"

    def setCluster(self, cluster_name=None):
        """set cluster
        
        :param cluster_name: [description], defaults to None
        :type cluster_name: [type], optional
        """        
        if not isNone(cluster_name):
            self._csite_ = cluster_name

    def getProjectSolution(self, proj_id, sol_id):
        """get projects solution
        
        :param proj_id: [description]
        :type proj_id: tuple
        :param sol_id: [description]
        :type sol_id: tuple
        :return: [description]
        :rtype: [type]
        """        
        self.url_dic = {'projects': proj_id, 'solutions': sol_id}
        return self.list()

    def getProjects(self):
        """get projects
        #TODO

        :return: projects dictionary
        :rtype: dict
        """        
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
        """get s3 proj id
        
        :param proj_code: [description]
        :type proj_code: tuple
        :return: return s3 project id
        :rtype: int
        """        
        projs = self.list()
        for proj in projs:
            if proj['name'] == proj_code:
                return proj['id']

    def getS3Keys(self, proj_code):
        """get s3 keys
        
        :param proj_code: [description]
        :type proj_code: tuple
        :return: return s3 key
        :rtype: [type]
        """        
        proj_id = self.getS3ProjId(proj_code)
        self.url_dic = {'projects': proj_id, 'key': ''}
        return self.list()

class api_key(GenericService):
    """api key
    #TODO
    
    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """    
    def __init__(self, debug=False):
        """constractor for this api_key class
        
        :param debug: [description], defaults to False
        :type debug: bool, optional
        """        
        GenericService.__init__(self, debug=debug)
        self._csite_ = "admin"

    def getInfo(self):
        """get info
        
        :return: [description]
        :rtype: [type]
        """        
        self.url_dic = {'api_key': 'api_key'}
        self._csite_ = 'admin'
        return self.list()


class iservice(GenericService):
    """iservice
    #TODO
    
    :param GenericService: [description]
    :type GenericService: [type]
    :return: [description]
    :rtype: [type]
    """    
    def __init__(self, api_key=api_key):
        GenericService.__init__(self, api_key=api_key, skip_session=True)

    def getAllProjects(self):
        self.url_dic = {"iservice": "user/all_wallet"}
        return self.list()
