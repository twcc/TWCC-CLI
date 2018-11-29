# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import GenericService
from twcc.services.base import projects
from twcc.util import pp, isNone, table_layout

chkPortPair = lambda x: True if type(x)==type({}) and len(set(['exposed', 'inner']).intersection(set(x.keys())) ) == 2 else False

class sites(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "k8s-taichung-default"
        self._api_key_ = api_key_tag
        self._cache_sol_ = {}

    def __del__(self):
        """
        @Todo design a cache to keep solutions
        """
        if self._debug_:
            print("__del__")

    @staticmethod
    def getGpuDefaultHeader():
        gpu_default = { 'bucket' : None,
            'replica' : "1",
            'command' : "whoami; sleep 600;",
            'flavor' : "10core40GBMemory1GPU" ,
            #'image' : "registry.twcc.ai/ngc/vtr:latest",
            #'image' : "registry.twcc.ai/ngc/nvidia/tensorflow-18.10-py2-v",
            #'image' : "registry.twcc.ai/ngc/nvidia/tensorflow-18.10-py2-v1",
            'image' : "registry.twcc.ai/ngc/nvidia/tensorflow-18.10-py2-v1:latest",
            # 'image' : "registry.twcc.ai/ngc/nvidia/tensorflow:latest", # for 160
            'gpfs01-mount-path' : "/mnt/home/work",
            'gpfs02-mount-path' : "/mnt/home/home"}
        return dict([ ("x-extra-property-%s"%(x), gpu_default[x]) for x in gpu_default.keys() ])

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

    def list(self):
        #print (self._project_id)
        self.ext_get = {'project': self._project_id}
        return self._do_api()


    def create(self, name, sol_id, extra_prop):
        self.twcc.header_extra = extra_prop
        self.http_verb = 'post'
        self.data_dic = {"name": name,
                "project": self._project_id,
                "solution": sol_id}
        #print(self.data_dic)
        #print(self.twcc.header_extra)
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
            table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))
        elif not isShow:
            return ans

    def _do_list_solution(self, sol_id):
        self.proj = projects(self._api_key_, self.twcc._debug)
        self.proj._csite_ = self._csite_

        ans = self.proj.getProjectSolution(self._project_id, sol_id)
        table_info = ans['site_extra_prop']
        self._cache_sol_[ sol_id ] = table_info


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
