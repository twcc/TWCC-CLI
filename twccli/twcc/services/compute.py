# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import json
from twcc.session import Session2
from twcc.services.generic import GpuService, CpuService
from twcc.services.base import projects, Flavors, iservice
from twcc.util import pp, isNone, table_layout, isDebug


def chkPortPair(x): return True if type(x) == type({}) and len(
    set(['exposed', 'inner']).intersection(set(x.keys()))) == 2 else False


class GpuSite(GpuService):

    def __init__(self, debug=False):
        GpuService.__init__(self)

        self._func_ = "sites"
        self._csite_ = Session2._getClusterName("CNTR")
        print(">"*10, "GpuSite", "<"*10, self._api_key_ )
        self._cache_sol_ = {}

    @staticmethod
    def getGpuList(mtype='list'):
        # @todo, python 3 is not good with dict key object
        gpu_list = [(0, '0 GPU + 01 cores + 008GB memory'), # twcc test only
                    (1, '1 GPU + 04 cores + 090GB memory'),
                    (2, '2 GPU + 08 cores + 180GB memory'),
                    (4, '4 GPU + 16 cores + 360GB memory'),
                    (8, '8 GPU + 32 cores + 720GB memory')]
        if mtype == 'list':
            return gpu_list
        elif mtype == 'dict':
            return dict(gpu_list)

    @staticmethod
    def getSolList(mtype='list', name_only=False, reverse=False):
        sol_list = [(4, "TensorFlow"),
                    (9, "Caffe2"),
                    (10, "Caffe"),
                    (13, "CNTK"),
                    (16, "CUDA"),
                    (19, "MXNet"),
                    (24, "PyTorch"),
                    # (29, "TensorRT"), # not avalible for now
                    # (35, "TensorRT_Server"), # not avalible for now
                    (42, "Theano"),
                    (49, "Torch"),
                    (52, "DIGITS")]

        if reverse:
            sol_list = [(y, x) for (x, y) in sol_list]

        if name_only and mtype == 'list':
            sol_list = [y for (x, y) in sol_list]

        if mtype == 'list':
            return sol_list
        elif mtype == 'dict' and not name_only:
            return dict(sol_list)

    def getCommitList(self, mtype='list'):
        self.func = 'image_commit'

        return self._do_api()

    @staticmethod
    def getGpuDefaultHeader(gpus=1):
        gpu_list = GpuSite.getGpuList(mtype='dict')
        if not gpus in gpu_list.keys():
            raise ValueError("GPU number '{0}' is not valid.".format(gpus))

        gpu_default = {
            # 'bucket' : None,
            'command': "whoami; sleep 600;",
            'flavor': gpu_list[gpus],
            'replica': '1',
        }
        return dict([("x-extra-property-%s" % (x), gpu_default[x]) for x in gpu_default.keys()])

    @staticmethod
    def mkS3MountFormat(alist):
        if len(alist) > 0:
            return json.dumps([{"name": x, "mountpath": "/mnt/s3/%s" % (x)} for x in alist])
        else:
            return "[]"

    @staticmethod
    def getIpBindAttr(port_mapping, pod_name="_UNDEF_"):
        default_assign_ip = {
            "action": "associateIP",
            "pod_name": pod_name,
            "ports": []}
        if len(port_mapping) > 0:
            for each_port in port_mapping:
                if chkPortPair(each_port):
                    port_map = {"targetPort": each_port['inner'],
                                "port": each_port['exposed']}
                    default_assign_ip['ports'].append(port_map)
                else:
                    raise ValueError(
                        "Port Mapping Error {0}".format(port_mapping))
            return default_assign_ip

    def getAvblS3(self, mtype='list'):
        res = self.list_solution(4, isShow=False)
        buckets = [x['name'] for x in res['bucket']]
        if mtype == 'list':
            return buckets
        elif mtype == 'dict':
            return dict([(x, "/mnt/s3/%s" % (x)) for x in buckets])

    def getAvblImg(self, sol_id, sol_name, latest_first=True):
        if sol_id:
            res = self.list_solution(sol_id, isShow=False)
            if latest_first:
                return sorted(res['image'], reverse=True)
            else:
                return res['image']
        else:
            raise ValueError(
                "Solution name:'{0}' is not available.".format(sol_name))

    def list(self, isAll=False):
        if isAll:
            self.ext_get = {'project': self._project_id,
                            "all_users": 1}
        else:
            self.ext_get = {'project': self._project_id}
        return self._do_api()

    def create(self, name, sol_id, extra_prop):

        # @todo change this
        extra_prop['x-extra-property-gpfs01-mount-path'] = '/mnt/work'
        extra_prop['x-extra-property-gpfs02-mount-path'] = '/home/{}'.format(
            self.twcc_session.twcc_username)

        self.twcc.header_extra = extra_prop
        self.http_verb = 'post'
        self.data_dic = {"name": name,
                         "desc": 'TWCC-Cli created GPU container',
                         "project": self._project_id,
                         "solution": sol_id}
        return self._do_api()

    def update(self, data_dic):
        self.http_verb = 'put'
        self.res_type = 'txt'
        self.data_dic = data_dic
        self.ext_get = None
        return self._do_api()

    def delete(self, site_id):
        self.http_verb = 'delete'
        self.res_type = 'txt'
        self.url_dic = {"sites": site_id}
        return self._do_api()

    def list_solution(self, sol_id, isShow=True):
        if sol_id in self._cache_sol_:
            ans = self._cache_sol_[sol_id]
        else:
            self._do_list_solution(sol_id)
            ans = self._cache_sol_[sol_id]

        if isShow:
            #table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))
            print(ans)
        elif not isShow:
            return ans

    def _do_list_solution(self, sol_id):
        self.proj = projects()
        self.proj._csite_ = self._csite_

        ans = self.proj.getProjectSolution(self._project_id, sol_id)
        table_info = ans['site_extra_prop']
        self._cache_sol_[sol_id] = table_info

    def getConnInfo(self, site_id, ssh_info=False):
        info_gen = self.queryById(site_id)

        info_detail = self.getDetail(site_id)
        #usr_name = Session2._whoami()[0]['username']
        usr_name = Session2._whoami()['username']

        info_port = [x for x in info_detail['Service'][0]['ports']]
        if not ssh_info:
            return info_port
        else:
            info_port = [x['port'] for x in info_detail['Service']
                        [0]['ports'] if x['target_port'] == 22][0]
            info_pub_ip = info_detail['Service'][0]['public_ip'][0]

            return "{}@{} -p {}".format(usr_name, info_pub_ip, info_port)

    def isReady(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "Ready"

    def getDetail(self, site_id):
        self.url_dic = {"sites": site_id, 'container': ""}
        self.http_verb = 'get'
        self.res_type = 'json'
        return self.list()

    def getPodName(self, site_id):
        detail = self.getDetail(site_id)
        if 'Pod' in detail and len(detail['Pod']) == 1 and detail['Pod'][0]['status'] == 'running':
            return detail['Pod'][0]['name']

    def exposedPort(self, site_id, port_id):
        pod_name = self.getPodName(site_id)
        bindAttr = {"action": "associateIP",
                    "pod_name": pod_name,
                    "ports": [{'targetPort': int(port_id)}]}
        self.url_dic = {"sites": site_id, 'container/action': ""}
        self.update(bindAttr)

    def unbindPort(self, site_id, port_id):
        pod_name = self.getPodName(site_id)
        unbindAttr = {"action": "disassociateIP",
                      "pod_name": pod_name,
                      "ports": [{'targetPort': int(port_id)}]}
        self.url_dic = {"sites": site_id, 'container/action': ""}
        self.update(unbindAttr)


class VcsSite(CpuService):
    def __init__(self):

        CpuService.__init__(self)

        self._func_ = "sites"
        self._csite_ = Session2._getClusterName("VCS")
        print(">"*10, "CpuSite", "<"*10, self._api_key_ )

    def list(self, isAll=False):
        if isAll:
            self.ext_get = {'project': self._project_id,
                            "all_users": 1}
        else:
            self.ext_get = {'project': self._project_id}

        return self._do_api()

    @staticmethod
    def getSolList(mtype='list', name_only=False, reverse=False):
        sol_list = [(60, "ubuntu"),
                    (177, "centos"), ]

        if reverse:
            sol_list = [(y, x) for (x, y) in sol_list]

        if name_only and mtype == 'list':
            sol_list = [y for (x, y) in sol_list]

        if mtype == 'list':
            return sol_list
        elif mtype == 'dict' and not name_only:
            return dict(sol_list)

    def _do_list_solution(self, sol_id):
        self.proj = projects()
        self.proj._csite_ = self._csite_

        return self.proj.getProjectSolution(self._project_id, sol_id)['site_extra_prop']

    def getFlavors(self):
        flv = Flavors(self._csite_)
        return dict([ (x['id'], x) for x in flv.list()])

    def getExtraProp(self, sol_id):
        extra_prop = self._do_list_solution(sol_id)


        # processing flavors
        extra_flv = set(extra_prop['flavor'])
        filter_flv = lambda x: True if x in extra_flv else False

        flvs = self.getFlavors()
        tflvs = dict([ (flvs[x]['id'], flvs[x]) for x in flvs if filter_flv(flvs[x]['name']) ])
        name2id = dict([ (tflvs[x]['name'], tflvs[x]['id']) for x in tflvs])
        tflvs_keys = tflvs.keys()

        products = self.getIsrvFlavors()
        wanted_pro = dict([ (x, products[x]['desc']) for x in products if x in tflvs_keys])

        # target: name to fid, fid to isrv name, flavor raw
        #pp(name2id=name2id)
        #pp(pro=wanted_pro)
        #pp(extra_flv=extra_flv)

        name2isrv = dict([ (wanted_pro[name2id[x]], x) for x in name2id])
        res = {}
        for ele in extra_prop:
            if ele == 'flavor':
                res["x-extra-property-{}".format(ele)] = name2isrv
            elif ele == 'image':
                res["x-extra-property-{}".format(ele)] = [ x.split(")")[1] for x in extra_prop[ele] if re.search('public', x) ]
            elif ele == 'system-volume-type':
                res["x-extra-property-{}".format(ele)] = { "hdd": "block_storage-hdd",
                        "ssd": "block_storage-ssd", "local": "local_disk"}
            else:
                res["x-extra-property-{}".format(ele)] = extra_prop[ele]
        return res


    def getIsrvFlavors(self, name_or_id= "flavor_id"):
        isrv = iservice()
        filter_flavor_id = lambda x: True if "flavor_id" in json.loads(x['other_content']) else False
        get_flavor_id = lambda x: int(json.loads(x['other_content'])['flavor_id'])

        fid_desc = dict([ (get_flavor_id(x), x) for x in isrv.getProducts() if filter_flavor_id(x) ])
        if name_or_id == "flavor_id":
            return fid_desc
        else:
            return dict([ (fid_desc[x]['desc'], fid_desc[x])for x in fid_desc])

    def create(self, name, sol_id, extra_prop):

        self.twcc.header_extra = extra_prop
        self.http_verb = 'post'
        self.data_dic = {"name": name,
                         "desc": 'TWCC-Cli created VCS',
                         "project": self._project_id,
                         "solution": sol_id}
        return self._do_api()
    def isReady(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "Ready"


class VcsSecurityGroup(CpuService):
    def __init__(self):
        CpuService.__init__(self)

        self._func_ = "security_groups"
        self._csite_ = Session2._getClusterName("VCS")
        print(">"*10, "CpuSite", "<"*10, self._api_key_ )

    def list(self, server_id=None):
        if not isNone(server_id):
            self.ext_get = {'project': self._project_id,
                    'server':server_id}
            return self._do_api()

    def addSecurityGroup(self, secg_id, port_num,
            cidr, protocol, direction):

        self.http_verb = "patch"
        self.url_dic = {"security_groups":secg_id}
        self.data_dic = {"project": self._project_id,
                "direction": direction,
                "protocol": protocol,
                "remote_ip_prefix": cidr,
                "port_range_max": port_num,
                "port_range_min": port_num}
        self._do_api()
    def deleteRule(self, rule_id):
        self.http_verb = "delete"
        self.ext_get = {'project': self._project_id}
        self._func_ = "security_group_rules"
        self.url_dic = {self._func_:rule_id}
        self._do_api()

        # processing flavors
        extra_flv = set(extra_prop['flavor'])
        filter_flv = lambda x: True if x in extra_flv else False

        flvs = self.getFlavors()
        tflvs = dict([ (flvs[x]['id'], flvs[x]) for x in flvs if filter_flv(flvs[x]['name']) ])
        name2id = dict([ (tflvs[x]['name'], tflvs[x]['id']) for x in tflvs])
        tflvs_keys = tflvs.keys()

        products = self.getIsrvFlavors()
        wanted_pro = dict([ (x, products[x]['desc']) for x in products if x in tflvs_keys])

        # target: name to fid, fid to isrv name, flavor raw
        #pp(name2id=name2id)
        #pp(pro=wanted_pro)
        #pp(extra_flv=extra_flv)

        name2isrv = dict([ (wanted_pro[name2id[x]], x) for x in name2id])
        res = {}
        for ele in extra_prop:
            if ele == 'flavor':
                res["x-extra-property-{}".format(ele)] = name2isrv
            elif ele == 'image':
                res["x-extra-property-{}".format(ele)] = [ x.split(")")[1] for x in extra_prop[ele] if re.search('public', x) ]
            elif ele == 'system-volume-type':
                res["x-extra-property-{}".format(ele)] = { "hdd": "block_storage-hdd",
                        "ssd": "block_storage-ssd", "local": "local_disk"}
            else:
                res["x-extra-property-{}".format(ele)] = extra_prop[ele]
        return res


    def getIsrvFlavors(self, name_or_id= "flavor_id"):
        isrv = iservice()
        filter_flavor_id = lambda x: True if "flavor_id" in json.loads(x['other_content']) else False
        get_flavor_id = lambda x: int(json.loads(x['other_content'])['flavor_id'])

        fid_desc = dict([ (get_flavor_id(x), x) for x in isrv.getProducts() if filter_flavor_id(x) ])
        if name_or_id == "flavor_id":
            return fid_desc
        else:
            return dict([ (fid_desc[x]['desc'], fid_desc[x])for x in fid_desc])

    def create(self, name, sol_id, extra_prop):

        self.twcc.header_extra = extra_prop
        self.http_verb = 'post'
        self.data_dic = {"name": name,
                         "desc": 'TWCC-Cli created VCS',
                         "project": self._project_id,
                         "solution": sol_id}
        return self._do_api()
    def isReady(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "Ready"


class VcsSecurityGroup(CpuService):
    def __init__(self):
        CpuService.__init__(self)

        self._func_ = "security_groups"
        self._csite_ = Session2._getClusterName("VCS")
        print(">"*10, "CpuSite", "<"*10, self._api_key_ )

    def list(self, server_id=None):
        if not isNone(server_id):
            self.ext_get = {'project': self._project_id,
                    'server':server_id}
            return self._do_api()

    def addSecurityGroup(self, secg_id, port_num,
            cidr, protocol, direction):

        self.http_verb = "patch"
        self.url_dic = {"security_groups":secg_id}
        self.data_dic = {"project": self._project_id,
                "direction": direction,
                "protocol": protocol,
                "remote_ip_prefix": cidr,
                "port_range_max": port_num,
                "port_range_min": port_num}
        self._do_api()
    def deleteRule(self, rule_id):
        self.http_verb = "delete"
        self.ext_get = {'project': self._project_id}
        self._func_ = "security_group_rules"
        self.url_dic = {self._func_:rule_id}
        self._do_api()

def getServerId(site_id):
    vcs = VcsSite()
    sites = vcs.queryById(site_id)
    if not 'id' in sites:
        raise ValueError("Site ID: {} is not found.".format(site_id))
    if len(sites['servers']) == 1:
        server_id = sites['servers'][0]
        return server_id


def getSecGroupList(site_id):
    server_id = getServerId(site_id)
    secg = VcsSecurityGroup()
    secg_list = secg.list(server_id=server_id)
    if len(secg_list) > 0:
        return secg_list[0]