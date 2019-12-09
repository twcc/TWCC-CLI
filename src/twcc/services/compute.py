# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import GenericService
from twcc.services.base import projects
from twcc.util import pp, isNone, table_layout

chkPortPair = lambda x: True if type(x)==type({}) and len(set(['exposed', 'inner']).intersection(set(x.keys())) ) == 2 else False

class sites(GenericService):
    # use default key_tag
    #def __init__(self, api_key_tag, debug=False):
    def __init__(self, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "k8s-taichung-default"
        self._cache_sol_ = {}

    def __del__(self):
        """
        @Todo design a cache to keep solutions
        """
        if self._debug_:
            print("__del__")

    @staticmethod
    def getGpuList(mtype='list'):
      #@todo, python 3 is not good with dict key object
      gpu_list = [ (1, '1 GPU + 04 cores + 090GB memory'),
           (2, '2 GPU + 08 cores + 180GB memory'),
           (4, '4 GPU + 16 cores + 360GB memory'),
           (8, '8 GPU + 32 cores + 720GB memory')]
      if mtype=='list':
          return gpu_list
      elif mtype=='dict':
          return dict(gpu_list)

    @staticmethod
    def getSolList(mtype='list', name_only=False, reverse=False):
        sol_list = [ (4, "TensorFlow"),
          (9, "Caffe2"),
          (10, "Caffe"),
          (13, "CNTK"),
          (16, "CUDA"),
          (19, "MXNet"),
          (24, "PyTorch"),
          #(29, "TensorRT"), # not avalible for now
          #(35, "TensorRT_Server"), # not avalible for now
          (42, "Theano"),
          (49, "Torch"),
          (52, "DIGITS") ]

        if reverse:
            sol_list = [ (y, x) for (x, y) in sol_list]

        if name_only and mtype=='list':
            sol_list = [ y for (x, y) in sol_list]

        if mtype=='list':
            return sol_list
        elif mtype=='dict' and not name_only:
            return dict(sol_list)

    def getCommitList(self, mtype='list'):
        self.func = 'image_commit';

        return self._do_api()

    @staticmethod
    def getGpuDefaultHeader(gpus=2):
        gpu_list = sites.getGpuList(mtype='dict')
        if not gpus in gpu_list.keys():
            raise ValueError("GPU number '{0}' is not valid.".format(gpus))

        gpu_default = {
            #'bucket' : None,
            'command' : "whoami; sleep 600;",
            'flavor' : gpu_list[gpus],
            'replica' : '1',
            }
        return dict([ ("x-extra-property-%s"%(x), gpu_default[x]) for x in gpu_default.keys() ])

    @staticmethod
    def mkS3MountFormat(alist):
        import json
        if len(alist)>0:
            return json.dumps([ {"name": x, "mountpath": "/mnt/s3/%s"%(x)} for x in alist])
        else:
            return "[]"

    @staticmethod
    def getIpBindAttr(port_mapping, pod_name = "_UNDEF_"):
        default_assign_ip = {
                "action": "associateIP",
                "pod_name": pod_name,
                "ports": [ ] }
        if len(port_mapping)>0:
            for each_port in port_mapping:
                if chkPortPair(each_port):
                    port_map = {"targetPort": each_port['inner'],
                                "port"  : each_port['exposed'] }
                    default_assign_ip['ports'].append(port_map)
                else:
                    raise ValueError("Port Mapping Error {0}".format(port_mapping))
            return default_assign_ip
    def getAvblS3(self, mtype='list'):
        res = self.list_solution(4, isShow=False)
        buckets = [ x['name'] for x in res['bucket']]
        if mtype=='list':
            return buckets
        elif mtype=='dict':
            return dict([ (x, "/mnt/s3/%s"%(x)) for x in buckets])

    def getAvblImg(self, sol_id, sol_name, latest_first=True):
        if sol_id:
            res = self.list_solution(sol_id, isShow=False)
            if latest_first:
                return sorted(res['image'], reverse=True)
            else:
                return res['image']
        else:
            raise ValueError("Solution name:'{0}' is not available.".format(sol_name))

    def list(self, isAll=False):
        if isAll:
            self.ext_get = {'project': self._project_id,
                "all_users": 1 }
        else:
            self.ext_get = {'project': self._project_id}
        return self._do_api()


    def create(self, name, sol_id, extra_prop):

        # @todo change this
        extra_prop['x-extra-property-gpfs01-mount-path'] = '/work/{}'.format(self._username)
        extra_prop['x-extra-property-gpfs02-mount-path'] = '/home/{}'.format(self._username)

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
        self.url_dic = {"sites":site_id}
        return self._do_api()

    def list_solution(self, sol_id, isShow=True):
        t_sol = None
        if sol_id in self._cache_sol_:
            t_sol = self._cache_sol_
        else:
            self._do_list_solution(sol_id)

        ans = self._cache_sol_[sol_id]
        if isShow:
            #table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))
            print(ans)
        elif not isShow:
            return ans

    def _do_list_solution(self, sol_id):
        self.proj = projects(self.twcc._debug)
        self.proj._csite_ = self._csite_

        ans = self.proj.getProjectSolution(self._project_id, sol_id)
        table_info = ans['site_extra_prop']
        self._cache_sol_[ sol_id ] = table_info

    def getConnInfo(self, site_id):
        info_gen = self.queryById(site_id)
        info_detail = self.getDetail(site_id)
        usr_name = info_gen['user']['username']
        info_port = [ x['port'] for x in info_detail['Service'][0]['ports'] if x['target_port'] == 22 ][0]
        info_pub_ip = info_detail['Service'][0]['public_ip'][0]

        return "{}@{} -p {}".format(usr_name, info_pub_ip, info_port)

    def isReady(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "Ready"

    def getDetail(self, site_id):
        self.url_dic = {"sites":site_id, 'container':""}
        self.http_verb = 'get'
        self.res_type = 'json'
        return self.list()

    def getPodName(self, site_id):
        detail = self.getDetail(site_id)
        if 'Pod' in detail and len(detail['Pod'])==1 and detail['Pod'][0]['status'] == 'running':
            return detail['Pod'][0]['name']

    def exposedPort(self, site_id, portAttr):
        self.url_dic = {"sites":site_id, 'container/action':""}
        self.update(portAttr)

    def unbindPort(self, site_id):
        pod_name = self.getPodName(site_id)
        unbindAttr = {"action": "disassociateIP",
                      "pod_name": pod_name}
        self.url_dic = {"sites":site_id, 'container/action':""}
        self.update(unbindAttr)
